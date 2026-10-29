"""Etapa 05 — Vista plana consolidada.

Lee `data/processed/tabla_normalizada.xlsx`, resuelve los identificadores de la
hoja `Objetos` a nombres y escribe
`data/processed/vista_plana_tabla_consolidada.xlsx`
(hoja 'Objetos - Concursos Tucumán').

Columnas: Concurso, Año, Expositora/Expositor, Ciudad, Provincia, Lugar en el
documento, ciudad_id, lat, lon, lat_provincia, lon_provincia, Categoría, N.º de
orden, Descripción del objeto, Fuera de concurso, Creación de la autora, Imagen,
Foto del álbum.

`Foto del álbum` es la foto del álbum de 1915 donde aparece la obra (la pone `04c`).

`Fuera de concurso` y `Creación de la autora` (`sí` / vacío) las pone `04f` leyendo el
texto del catálogo, que sigue entero en `Descripción del objeto`.

`lat`/`lon` es el punto de la ciudad y `lat_provincia`/`lon_provincia` el de la
capital de su provincia (los pone `04d`): lo que sólo tiene provincia, o una ciudad
sin punto seguro, igual se puede ubicar a nivel provincia.

`Lugar en el documento` es la procedencia tal como la escribió el catálogo
("SANTIAGO", "SANTIAGO DEL ESTERO", "ASILO, CIUDAD"), tomada de
`data/interim/objetos_crudos.csv` (etapa 01). Va al lado del lugar normalizado para
poder cotejar contra la fuente sin cruzar hojas, y `ciudad_id` deja ver cuándo dos
lugares escritos distinto son la misma fila de `Ciudades` (o no). Pedido de Larisa,
2026-10: "no entiendo de dónde son las referencias, está desagregada".

Orden de filas: Concurso (1915 → 1916), Categoría (alfabético), Expositora
(alfabético, sensible a mayúsculas); dentro de cada grupo, el orden del catálogo
(`objeto_id`), no el N.º de orden.

Se regenera a partir de la tabla normalizada tal cual está: cualquier corrección
hecha a mano en `tabla_normalizada.xlsx` (categorías, ids de expositora, texto de
objeto, etc.) se ve reflejada acá.
"""
from __future__ import annotations

import pandas as pd

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
CRUDOS = INTERIM / "objetos_crudos.csv"  # salida de 01_ingesta: texto original
SALIDA = PROCESSED / "vista_plana_tabla_consolidada.xlsx"
HOJA = "Objetos - Concursos Tucumán"

COLS = ["Concurso", "Año", "Expositora/Expositor", "Ciudad", "Provincia",
        "Lugar en el documento", "ciudad_id", "lat", "lon", "lat_provincia", "lon_provincia",
        "Categoría", "N.º de orden", "Descripción del objeto", "Fuera de concurso",
        "Creación de la autora", "Imagen del catálogo", "Foto del álbum"]


def _hoja(xl: pd.ExcelFile, prefijo: str) -> pd.DataFrame:
    nombre = next(s for s in xl.sheet_names if s.startswith(prefijo))
    return xl.parse(nombre)


def lugar_original(obj: pd.DataFrame, crudos=CRUDOS) -> pd.Series:
    """Procedencia tal como figura en el catálogo, por objeto_id.

    `objetos_crudos.csv` y la tabla normalizada numeran los objetos igual (las dos
    salen del mismo Excel, en el mismo orden). Si eso se rompe, el texto quedaría
    pegado al objeto equivocado: mejor frenar que mezclar.
    """
    c = pd.read_csv(crudos)
    if set(c["objeto_id"]) != set(obj["objeto_id"]):
        raise ValueError(f"{crudos.name} y la hoja Objetos no tienen los mismos objeto_id")
    return obj["objeto_id"].map(c.set_index("objeto_id")["ciudad_raw"])


def construir(fuente=FUENTE) -> pd.DataFrame:
    xl = pd.ExcelFile(fuente)
    obj = _hoja(xl, "Objetos")
    con = _hoja(xl, "Concurso")
    exp = _hoja(xl, "Expositora")
    cat = _hoja(xl, "Categor")
    ciu = _hoja(xl, "Ciudad")

    exp_col = "Nombre" if "Nombre" in exp.columns else exp.columns[1]

    df = obj.merge(con[["concurso_id", "anio", "nombre"]], on="concurso_id", how="left")
    df = df.merge(exp[["persona_id", exp_col]].rename(columns={"persona_id": "expositora_id"}),
                  on="expositora_id", how="left")
    df = df.merge(cat, on="categoria_id", how="left")
    cols_ciu = ["ciudad_id", "nombre_ciudad", "nombre_provincia"]
    cols_ciu += [c for c in ("lat", "lon", "lat_provincia", "lon_provincia") if c in ciu.columns]
    df = df.merge(ciu[cols_ciu], on="ciudad_id", how="left")
    # ciudad desconocida (ids 5, 8, 9, 10): se muestra la provincia
    ciudad = df["nombre_ciudad"].where(
        df["nombre_ciudad"].notna() & (df["nombre_ciudad"].astype(str).str.strip() != ""),
        df["nombre_provincia"])

    out = pd.DataFrame({
        "Concurso": df["nombre"],
        "Año": df["anio"],
        "Expositora/Expositor": df[exp_col],
        "Ciudad": ciudad,
        "Provincia": df["nombre_provincia"],
        "Lugar en el documento": lugar_original(df),
        "ciudad_id": df["ciudad_id"],
        "lat": df["lat"] if "lat" in df.columns else pd.NA,
        "lon": df["lon"] if "lon" in df.columns else pd.NA,
        "lat_provincia": df["lat_provincia"] if "lat_provincia" in df.columns else pd.NA,
        "lon_provincia": df["lon_provincia"] if "lon_provincia" in df.columns else pd.NA,
        "Categoría": df["nombre_categoria"],
        "N.º de orden": df["ORDEN"],
        "Descripción del objeto": df["OBJETO"],
        "Fuera de concurso": df["fuera_de_concurso"] if "fuera_de_concurso" in df.columns else pd.NA,
        "Creación de la autora": df["creacion_autora"] if "creacion_autora" in df.columns else pd.NA,
        "Imagen del catálogo": df["imagen"] if "imagen" in df.columns else pd.NA,
        "Foto del álbum": df["foto_album"] if "foto_album" in df.columns else pd.NA,
    })

    # Concurso, Categoría y Expositora (alfabético, sensible a mayúsculas).
    # Dentro de un mismo grupo se conserva el orden del catálogo (objeto_id),
    # no el N.º de orden.
    out = out.sort_values(
        by=["Año", "Categoría", "Expositora/Expositor"],
        kind="stable",
        key=lambda c: c if c.name == "Año"
        else c.map(lambda x: "" if pd.isna(x) else str(x)),
    ).reset_index(drop=True)
    return out[COLS]


def main() -> None:
    out = construir()
    out.to_excel(SALIDA, sheet_name=HOJA, index=False)
    print(f"{len(out)} filas -> {SALIDA}")


if __name__ == "__main__":
    main()
