"""Etapa 05 — Vista plana consolidada.

Lee `data/processed/tabla_normalizada.xlsx`, resuelve los identificadores de la
hoja `Objetos` a nombres y escribe
`data/processed/vista_plana_tabla_consolidada.xlsx`
(hoja 'Objetos - Concursos Tucumán').

Columnas: Concurso, Año, Expositora/Expositor, Ciudad, lat, lon, Categoría,
N.º de orden, Descripción del objeto, Imagen.
Orden de filas: Concurso (1915 → 1916), Categoría (alfabético), Expositora
(alfabético, sensible a mayúsculas), N.º de orden.

Se regenera a partir de la tabla normalizada tal cual está: cualquier corrección
hecha a mano en `tabla_normalizada.xlsx` (categorías, ids de expositora, texto de
objeto, etc.) se ve reflejada acá.
"""
from __future__ import annotations

import pandas as pd

from _util import PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SALIDA = PROCESSED / "vista_plana_tabla_consolidada.xlsx"
HOJA = "Objetos - Concursos Tucumán"

COLS = ["Concurso", "Año", "Expositora/Expositor", "Ciudad", "lat", "lon",
        "Categoría", "N.º de orden", "Descripción del objeto", "Imagen"]


def _hoja(xl: pd.ExcelFile, prefijo: str) -> pd.DataFrame:
    nombre = next(s for s in xl.sheet_names if s.startswith(prefijo))
    return xl.parse(nombre)


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
    cols_ciu += [c for c in ("lat", "lon") if c in ciu.columns]
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
        "lat": df["lat"] if "lat" in df.columns else pd.NA,
        "lon": df["lon"] if "lon" in df.columns else pd.NA,
        "Categoría": df["nombre_categoria"],
        "N.º de orden": df["ORDEN"],
        "Descripción del objeto": df["OBJETO"],
        "Imagen": df["imagen"] if "imagen" in df.columns else pd.NA,
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
