"""Etapa 10: Técnicas y materiales de cada obra, como dato de la base.

Hasta el 30/10 las técnicas y los materiales sólo existían dentro del explorador. Ahora
quedan en la hoja `Objetos` (y de ahí en la vista plana), con las mismas reglas que usa
`14` (`_tecnicas.py`, sobre `decisiones/tecnicas_materiales.csv`, revisada por LM):

    tecnicas         etiquetas separadas por "; " (Encaje; Encaje de bolillos). Un
                     subtipo lleva también su técnica general. Vacío = sin técnica indicada
    tecnica_origen   de dónde sale: "texto de la obra", "categoría del catálogo" (el texto
                     no nombra ninguna y la sección sí, `tecnica_por_categoria`) o "sin dato"
    materiales       etiquetas separadas por "; "; incluye el que nombra la sección del
                     catálogo (Chales de vicuña -> Vicuña)

Son etiquetas que agrega el proyecto al lado del texto del catálogo (`OBJETO`), que no se
toca.

Entrada : data/processed/tabla_normalizada.xlsx (Objetos)
          data/interim/decisiones/tecnicas_materiales.csv, familias_categorias.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Objetos con esas columnas
"""
from __future__ import annotations

from collections import Counter

import pandas as pd

from _tecnicas import MAT, ORIGEN, TEC, familias, materiales, tecnicas
from _util import PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
COLS = ["tecnicas", "tecnica_origen", "materiales"]


def etiquetar(objeto, categoria_id, F: pd.DataFrame) -> tuple[str, str, str]:
    txt = "" if pd.isna(objeto) else str(objeto)
    fam = F.loc[categoria_id] if categoria_id in F.index else None
    tec, ts = tecnicas(txt, fam["tecnica_por_categoria"] if fam is not None else "")
    mat = materiales(txt, fam["material_por_categoria"] if fam is not None else "")
    return ("; ".join(TEC[k] for k in tec if k != "sin"), ORIGEN[ts],
            "; ".join(MAT[k] for k in mat))


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    O = hojas["Objetos"].drop(columns=COLS, errors="ignore")
    F = familias()

    O[COLS] = pd.DataFrame([etiquetar(o, c, F) for o, c in zip(O["OBJETO"], O["categoria_id"])],
                           index=O.index)
    hojas["Objetos"] = O
    print(f"{len(O)} obras · técnica según: {dict(Counter(O['tecnica_origen']))} · "
          f"con material: {(O['materiales'] != '').sum()}")

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
