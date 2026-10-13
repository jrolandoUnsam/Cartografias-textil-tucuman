"""Etapa 04d — Ubicación de las ciudades.

`data/interim/decisiones/coordenadas_ciudades.csv` es la tabla de decisión de las
ciudades (cargada a mano, ver `src/pipeline/README.md`) y es la ÚNICA fuente de todo lo
que dice dónde queda cada una:

    nombre_ciudad_hoy, nombre_provincia   topónimo actual y provincia
    lat, lon                              punto de la ciudad
    lat_provincia, lon_provincia          punto de la capital de la provincia, para
                                          ubicar también lo que sólo tiene provincia
    precision                             vacío = segura; "tentativa" si no es seguro
    nota                                  por qué se decidió así (p. ej. "LM 9-10: …")

Hasta 2026-10-12 este script sólo tomaba `lat`/`lon` y el nombre actual y la provincia
salían de la tabla manual, que tenía su propia copia: las dos llegaron a diferir
("Villa Vitulumba" en la tabla, "Villa Tulumba" en el CSV). Ahora el CSV pisa esas dos
columnas de la hoja `Ciudades`; `nombre_ciudad` (cómo lo escribió el catálogo) no se
toca.

Ciudades sin coordenada cargada (nombre ambiguo, desconocido, o pendiente todavía)
quedan con `lat`/`lon` vacíos.

Entrada : data/processed/tabla_normalizada.xlsx (hoja Ciudades)
          data/interim/decisiones/coordenadas_ciudades.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Ciudades con esas columnas
          (sobreescribe el archivo, respetando las demás hojas)
"""
from __future__ import annotations

import pandas as pd

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
DECISION = INTERIM / "decisiones" / "coordenadas_ciudades.csv"
COLS_DECISION = ["nombre_ciudad_hoy", "nombre_provincia", "lat", "lon",
                 "lat_provincia", "lon_provincia", "precision", "nota"]


def main() -> None:
    dec = pd.read_csv(DECISION)
    faltan = [c for c in ["ciudad_id"] + COLS_DECISION if c not in dec.columns]
    if faltan:
        raise ValueError(f"{DECISION.name}: faltan las columnas {faltan}")
    dec = dec[["ciudad_id"] + COLS_DECISION]

    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    nombre_hoja = next(s for s in xl.sheet_names if s.startswith("Ciudad"))
    C = hojas[nombre_hoja]

    sin_decision = sorted(set(C["ciudad_id"]) - set(dec["ciudad_id"]))
    if sin_decision:
        print(f"AVISO — ciudades sin fila en {DECISION.name}: {sin_decision}")

    C = C.drop(columns=[c for c in COLS_DECISION if c in C.columns])
    C = C.merge(dec, on="ciudad_id", how="left")
    hojas[nombre_hoja] = C

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)

    total = len(C)
    con_coord = C["lat"].notna().sum()
    con_prov = C["lat_provincia"].notna().sum()
    print(f"{con_coord}/{total} ciudades con coordenadas "
          f"({total - con_coord} sin coordenada cargada todavía)")
    print(f"{con_prov}/{total} con punto de provincia")
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
