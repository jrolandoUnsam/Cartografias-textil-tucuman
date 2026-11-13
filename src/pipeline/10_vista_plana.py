"""Etapa 10: Vista plana consolidada.

Lee `data/processed/tabla_normalizada.xlsx`, resuelve los identificadores de la
hoja `Objetos` a nombres y escribe
`data/processed/vista_plana_tabla_consolidada.xlsx`
(hoja 'Objetos - Concursos Tucumán').

Columnas: Concurso, Año, Expositora/Expositor, Género, Ciudad, Provincia, Lugar en el
documento, ciudad_id, lat, lon, lat_provincia, lon_provincia, Categoría (tal como la
imprimió el catálogo), N.º de orden, Descripción del objeto, Técnicas, Técnica según, Materiales (las pone `09`), Fuera de concurso,
Creación de la autora, Imagen del catálogo, Foto del álbum, En la prensa.

`Género` es el de la hoja `Expositoras` (F, M o I = institución).

`Foto del álbum` es la foto del álbum de 1915 donde aparece la obra (la pone `05`).

`En la prensa` lista las notas de época (`decisiones/menciones_prensa.csv`) que nombran
la obra o hablan de su expositora: diario, fecha y título, separadas por " | ".

`Fuera de concurso` y `Creación de la autora` (`sí` / vacío) las pone `08` leyendo el
texto del catálogo, que sigue entero en `Descripción del objeto`.

`lat`/`lon` es el punto de la ciudad y `lat_provincia`/`lon_provincia` el de la
capital de su provincia (los pone `06`): lo que sólo tiene provincia, o una ciudad
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

from _util import DECISIONES, INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
PRENSA = DECISIONES / "menciones_prensa.csv"
CRUDOS = INTERIM / "objetos_crudos.csv"  # salida de 01_ingesta: texto original
SALIDA = PROCESSED / "vista_plana_tabla_consolidada.xlsx"
HOJA = "Objetos - Concursos Tucumán"

COLS = ["Concurso", "Año", "Expositora/Expositor", "Género", "Ciudad", "Provincia",
        "Lugar en el documento", "ciudad_id", "lat", "lon", "lat_provincia", "lon_provincia",
        "Categoría", "N.º de orden",
        "Descripción del objeto", "Técnicas", "Técnica según", "Materiales", "Fuera de concurso",
        "Creación de la autora", "Imagen del catálogo", "Foto del álbum", "En la prensa"]


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


def en_la_prensa(df: pd.DataFrame, xl: pd.ExcelFile, prensa=PRENSA) -> pd.Series:
    """Menciones de prensa de cada obra: las que nombran la obra y las que hablan de su
    expositora ("sobre la expositora", solo en sus obras del concurso del año de la
    nota). Las de un lugar no se copian a sus obras; las
    descartadas en la revisión (`mostrar` = no) no van. Mismo criterio que el explorador."""
    fuentes = xl.parse("Fuentes")
    diario = {int(f): str(d).split(",")[0].strip() for f, d in zip(fuentes.fuente_id, fuentes.descripcion)}
    de_obra, de_persona = {}, {}
    for m in pd.read_csv(prensa, encoding="utf-8-sig", dtype=str, keep_default_na=False).itertuples():
        if m.mostrar.strip().lower() == "no":
            continue
        y, mes, d = m.fecha.split("-")
        ref = f"{diario.get(int(m.fuente_id), '')}, {int(d)}/{int(mes)}/{y}, «{m.titulo}»"
        oids = [int(x) for x in m.objeto_id.split(";") if x.strip()]
        for oid in oids:
            de_obra.setdefault(oid, []).append(ref)
        if m.persona_id and not oids:  # solo en sus obras del concurso de ese año
            de_persona.setdefault((int(float(m.persona_id)), int(y)), []).append(f"{ref} (sobre la expositora)")
    textos = [de_obra.get(o, []) + de_persona.get((p, a), [])
              for o, p, a in zip(df["objeto_id"], df["expositora_id"], df["anio"])]
    return pd.Series([" | ".join(t) or pd.NA for t in textos], index=df.index)


def construir(fuente=FUENTE) -> pd.DataFrame:
    xl = pd.ExcelFile(fuente)
    obj = _hoja(xl, "Objetos")
    con = _hoja(xl, "Concurso")
    exp = _hoja(xl, "Expositora")
    cat = _hoja(xl, "Categor")
    ciu = _hoja(xl, "Ciudad")

    exp_col = "Nombre" if "Nombre" in exp.columns else exp.columns[1]

    df = obj.merge(con[["concurso_id", "anio", "nombre"]], on="concurso_id", how="left")
    cols_exp = ["persona_id", exp_col] + (["Género"] if "Género" in exp.columns else [])
    df = df.merge(exp[cols_exp].rename(columns={"persona_id": "expositora_id"}),
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
        "Género": df["Género"] if "Género" in df.columns else pd.NA,
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
        "Técnicas": df["tecnicas"] if "tecnicas" in df.columns else pd.NA,
        "Técnica según": df["tecnica_origen"] if "tecnica_origen" in df.columns else pd.NA,
        "Materiales": df["materiales"] if "materiales" in df.columns else pd.NA,
        "Fuera de concurso": df["fuera_de_concurso"] if "fuera_de_concurso" in df.columns else pd.NA,
        "Creación de la autora": df["creacion_autora"] if "creacion_autora" in df.columns else pd.NA,
        "Imagen del catálogo": df["imagen"] if "imagen" in df.columns else pd.NA,
        "Foto del álbum": df["foto_album"] if "foto_album" in df.columns else pd.NA,
        "En la prensa": en_la_prensa(df, xl),
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
