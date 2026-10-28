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

Además, en `Objetos`: si una expositora tiene obras donde el catálogo escribió sólo la
provincia ("TUCUMÁN") y otras con una localidad de esa provincia (San Miguel de
Tucumán), las primeras pasan a esa localidad. La ciudad del catálogo queda en
`ciudad_id_catalogo`, y el texto original sigue en "Lugar en el documento" de la vista
plana.

Entrada : data/processed/tabla_normalizada.xlsx (hoja Ciudades)
          data/interim/decisiones/coordenadas_ciudades.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Ciudades con esas columnas y
          Objetos con `ciudad_id_catalogo` (sobreescribe el archivo, respetando las
          demás hojas)
"""
from __future__ import annotations

import pandas as pd
from unidecode import unidecode

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
DECISION = INTERIM / "decisiones" / "coordenadas_ciudades.csv"
COLS_DECISION = ["nombre_ciudad_hoy", "nombre_provincia", "lat", "lon",
                 "lat_provincia", "lon_provincia", "precision", "nota"]


def solo_provincia(C: pd.DataFrame) -> pd.Series:
    """Ciudades donde el catálogo escribió sólo la provincia ("TUCUMÁN", "CATAMARCA") o
    nada: `nombre_ciudad` vacío o igual a la provincia. Una localidad todavía sin
    coordenadas (Los Mendoza) no cuenta: dice más que la provincia."""
    def norm(s):
        return unidecode(str(s)).strip().lower() if pd.notna(s) else ""
    return C["nombre_provincia"].notna() & (
        C["nombre_ciudad"].isna() | (C["nombre_ciudad"].map(norm) == C["nombre_provincia"].map(norm)))


def localidad_de_la_expositora(O: pd.DataFrame, C: pd.DataFrame) -> pd.DataFrame:
    """Si una expositora tiene obras con sólo la provincia y otras con una localidad de
    esa misma provincia, las primeras pasan a esa localidad (Julián, 2026-10-28).
    `ciudad_id_catalogo` guarda la ciudad que escribió el catálogo; vacío = sin cambio.
    Si hay dos localidades posibles no se elige ninguna y se avisa."""
    O = O.copy()
    if "ciudad_id_catalogo" in O.columns:  # corrida repetida de 04d: se parte de lo del catálogo
        previo = O["ciudad_id_catalogo"].notna()
        O.loc[previo, "ciudad_id"] = O.loc[previo, "ciudad_id_catalogo"].astype(int)
    O["ciudad_id_catalogo"] = pd.Series(pd.NA, index=O.index, dtype="Int64")
    prov = C.set_index("ciudad_id")["nombre_provincia"]
    solo = set(C.loc[solo_provincia(C), "ciudad_id"])
    nombre = C.set_index("ciudad_id")["nombre_ciudad"]
    movidas = 0
    for pid, g in O.groupby("expositora_id"):
        for cid in sorted(set(g["ciudad_id"]) & solo):
            destino = sorted({c for c in g["ciudad_id"] if c not in solo and prov.get(c) == prov[cid]})
            if len(destino) > 1:
                print(f"  AVISO — expositora {pid}: '{prov[cid]}' a secas y varias localidades "
                      f"{[nombre[c] for c in destino]}; no se mueve")
                continue
            if destino:
                fila = (O["expositora_id"] == pid) & (O["ciudad_id"] == cid)
                O.loc[fila, "ciudad_id_catalogo"] = cid
                O.loc[fila, "ciudad_id"] = destino[0]
                movidas += int(fila.sum())
                print(f"  expositora {pid}: {int(fila.sum())} obras de '{prov[cid]}' -> {nombre[destino[0]]}")
    print(f"{movidas} obras pasan de la provincia a la localidad de la misma expositora\n")
    return O


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
    hojas["Objetos"] = localidad_de_la_expositora(hojas["Objetos"], C)

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
