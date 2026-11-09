"""Etapa 09: Categorías normalizadas.

`data/interim/decisiones/categorias.csv` agrega a cada sección del catálogo su nombre
normalizado, sin tocar `nombre_categoria` (el nombre tal como lo imprimió cada concurso):

    categoria_norm         la sección dentro de su propio catálogo. Sólo une las que son
                           una misma serie partida en dos títulos: la numeración sigue de
                           una a otra (Chales de vicuña 1-22 → Chales y echarpes 23-41;
                           Jergones y sobrepelos 1-25 → Jergones 26-36)
    criterio               por qué, con la evidencia del catálogo
    estado                 "propuesta" hasta que la revise LM

No es la `familia` de `familias_categorias.csv` (tipo de obra, más gruesa).

Entrada : data/processed/tabla_normalizada.xlsx (hoja Categorías)
          data/interim/decisiones/categorias.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Categorías con esas columnas
"""
from __future__ import annotations

import sys

import pandas as pd

from _util import DECISIONES, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
DECISION = DECISIONES / "categorias.csv"
COLS = ["categoria_norm", "criterio", "estado"]
# la columna `categoria_comparable` (equivalencias entre 1915 y 1916) se quitó el 30/10


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    C = hojas["Categorías"].drop(columns=COLS + ["categoria_comparable"], errors="ignore")
    D = pd.read_csv(DECISION)

    faltan = sorted(set(C["categoria_id"]) - set(D["categoria_id"]))
    if faltan:
        sys.exit(f"ERROR: categorías sin fila en {DECISION.name}: {faltan}")
    distinto = C.merge(D, on="categoria_id", suffixes=("", "_csv"))
    distinto = distinto[distinto["nombre_categoria"] != distinto["nombre_categoria_csv"]]
    for _, r in distinto.iterrows():
        print(f"  AVISO: categoría {r.categoria_id}: la tabla dice '{r.nombre_categoria}' "
              f"y el CSV '{r.nombre_categoria_csv}'")

    hojas["Categorías"] = C.merge(D[["categoria_id", *COLS]], on="categoria_id", how="left")
    print(f"{len(C)} secciones -> {D['categoria_norm'].nunique()} normalizadas "
          f"({(D['estado'] == 'propuesta').sum()} en propuesta)")

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
