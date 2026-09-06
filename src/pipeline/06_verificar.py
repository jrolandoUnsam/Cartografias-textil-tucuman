"""Etapa 06 — Verificación.

Compara las salidas de `data/processed/` y `data/intermid/revision_duplicados.xlsx`
contra las copias congeladas de `tests/golden/`, hoja por hoja, y reporta diferencias.
"""
from __future__ import annotations

import sys

import pandas as pd

from _util import GOLDEN, INTERIM, PROCESSED  # noqa: F401  (intermid -> interim, ya migrado)

PARES = [
    (PROCESSED / "tabla_normalizada.xlsx", GOLDEN / "tabla_normalizada.xlsx"),
    (PROCESSED / "vista_plana_tabla_consolidada.xlsx", GOLDEN / "vista_plana_tabla_consolidada.xlsx"),
    (INTERIM / "revision_duplicados.xlsx", GOLDEN / "revision_duplicados.xlsx"),
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
