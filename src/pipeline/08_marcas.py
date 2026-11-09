"""Etapa 08: Marcas de cada objeto que el catálogo dice en el texto.

Agrega a la hoja `Objetos` dos columnas (`sí` / vacío), leídas de `OBJETO`, que es el
texto del catálogo y no se toca:

    fuera_de_concurso    el catálogo dice "(fuera de concurso)": la obra se exhibió
                         pero no compitió (2 obras de 1916, crochet)
    creacion_autora      el catálogo dice "creación de la autora": diseño propio, no un
                         modelo tradicional (12 obras)

Pedido de Julián, 2026-10-25: que queden como dato aparte para poder filtrarlas sin
perder lo que dice la fuente.

Entrada : data/processed/tabla_normalizada.xlsx (hoja Objetos)
Salida  : data/processed/tabla_normalizada.xlsx, hoja Objetos con esas dos columnas
"""
from __future__ import annotations

import pandas as pd
from unidecode import unidecode

from _util import PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
MARCAS = {
    "fuera_de_concurso": r"fuera de concurso",
    "creacion_autora": r"creacion de la autora",
}


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    O = hojas["Objetos"]
    texto = O["OBJETO"].fillna("").map(lambda s: unidecode(str(s)).lower())
    for col, patron in MARCAS.items():
        O[col] = texto.str.contains(patron, regex=True).map({True: "sí", False: None})
        print(f"{col}: {(O[col] == 'sí').sum()} objetos")
    hojas["Objetos"] = O

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
