"""Etapa 06 — Verificación.

Compara las salidas de `data/processed/` contra las copias congeladas de
`tests/golden/`, hoja por hoja, y reporta diferencias.

`data/interim/revision_duplicados.xlsx` no se compara: es un insumo anotado a mano
(la semilla de `03_candidatos`), no algo que el pipeline escriba.
"""
from __future__ import annotations

import sys

import pandas as pd

from _util import GOLDEN, PROCESSED

PARES = [
    (PROCESSED / "tabla_normalizada.xlsx", GOLDEN / "tabla_normalizada.xlsx"),
    (PROCESSED / "vista_plana_tabla_consolidada.xlsx", GOLDEN / "vista_plana_tabla_consolidada.xlsx"),
]


def comparar(actual, esperado) -> bool:
    if not actual.exists():
        print(f"  FALTA generar: {actual.name}")
        return False
    a, e = pd.ExcelFile(actual), pd.ExcelFile(esperado)
    ok = True
    for hoja in e.sheet_names:
        da = a.parse(hoja, header=None) if hoja in a.sheet_names else None
        de = e.parse(hoja, header=None)
        if da is None:
            print(f"  [{hoja}] falta la hoja"); ok = False; continue
        if da.shape != de.shape:
            print(f"  [{hoja}] shape {da.shape} != golden {de.shape}"); ok = False; continue
        difs = (da.fillna("__NA__").astype(str).values != de.fillna("__NA__").astype(str).values)
        if difs.any():
            print(f"  [{hoja}] {difs.sum()} celdas distintas"); ok = False
        else:
            print(f"  [{hoja}] OK")
    return ok


def main() -> None:
    todo_ok = True
    for actual, esperado in PARES:
        print(actual.name)
        todo_ok &= comparar(actual, esperado)
    sys.exit(0 if todo_ok else 1)


if __name__ == "__main__":
    main()
