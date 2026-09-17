"""Etapa 04d — Coordenadas de las ciudades.

`data/interim/decisiones/coordenadas_ciudades.csv` es una tabla de decisión manual
(cargada a mano por la investigadora, ver `src/pipeline/README.md`) con `ciudad_id`,
`lat`, `lon`. Este script la cruza contra la hoja `Ciudades` de `tabla_normalizada.xlsx`
y le agrega las columnas `lat`/`lon`, para poder ubicar cada ciudad en un mapa.

Ciudades sin coordenada cargada (nombre ambiguo, desconocido, o pendiente todavía)
quedan con `lat`/`lon` vacíos.

Entrada : data/processed/tabla_normalizada.xlsx (hoja Ciudades)
          data/interim/decisiones/coordenadas_ciudades.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Ciudades con columnas
          `lat`/`lon` agregadas (sobreescribe el archivo, respetando las demás hojas)
"""
from __future__ import annotations

import pandas as pd

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
DECISION = INTERIM / "decisiones" / "coordenadas_ciudades.csv"


def main() -> None:
    coords = pd.read_csv(DECISION)[["ciudad_id", "lat", "lon"]]

    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    nombre_hoja = next(s for s in xl.sheet_names if s.startswith("Ciudad"))
    C = hojas[nombre_hoja]

    C = C.drop(columns=[c for c in ("lat", "lon") if c in C.columns])
    C = C.merge(coords, on="ciudad_id", how="left")
    hojas[nombre_hoja] = C

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)

    total = len(C)
    con_coord = C["lat"].notna().sum()
    print(f"{con_coord}/{total} ciudades con coordenadas "
          f"({total - con_coord} sin coordenada cargada todavía)")
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
