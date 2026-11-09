"""Técnicas y materiales de una obra, leídos de su texto. Lo usan `10` (columnas de la
base) y `14` (explorador), así las dos salidas dicen lo mismo.

Las reglas están en `decisiones/tecnicas_materiales.csv`, revisada por LM (28/10/2026):
etiqueta, técnica general (`grupo`), `patron` y `excepto` sobre el texto sin tildes y en
minúsculas. Los términos sin `clave` (puntilla, tejido a mano, hilado, teñido) no se usan.
Si el texto no nombra ninguna técnica se usa la de la categoría
(`familias_categorias.csv`, `tecnica_por_categoria`); si tampoco hay, "Sin
identificar". El texto del catálogo no se toca.
"""
from __future__ import annotations

import re

import pandas as pd
from unidecode import unidecode

from _util import DECISIONES

TECNICAS = DECISIONES / "tecnicas_materiales.csv"
FAMILIAS = DECISIONES / "familias_categorias.csv"

# Técnicas que no salen de las reglas: la de la categoría cuando no se puede precisar,
# y la falta de dato.
TEC_SIN_REGLA = {"encrand": "Encaje o randa (sin precisar)",
                 "bordesh": "Bordado o deshilado (sin precisar)", "sin": "Sin identificar"}

# de dónde sale la técnica de una obra
ORIGEN = {"o": "texto de la obra", "c": "categoría del catálogo", "n": "sin dato"}


def clave(s) -> str:
    return re.sub(r"\s+", " ", unidecode(str(s or "")).lower()).strip()


def leer_csv(ruta) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def leer_reglas() -> tuple[dict, dict, dict, list]:
    """Etiquetas de técnicas y materiales, la técnica general de cada subtipo
    (Encaje de bolillos -> Encaje) y las reglas."""
    T = leer_csv(TECNICAS)
    T = T[T["clave"] != ""]
    tec, mat, grupo, reglas = {}, {}, {}, []
    for r in T.itertuples():
        (tec if r.tipo == "técnica" else mat).setdefault(r.clave, r.etiqueta)
        if r.grupo:
            grupo[r.clave] = r.grupo
        reglas.append((r.tipo, r.clave, re.compile(r.patron), re.compile(r.excepto) if r.excepto else None))
    return {**tec, **TEC_SIN_REGLA}, mat, grupo, reglas


TEC, MAT, GRUPO, REGLAS = leer_reglas()


def hallar(tipo: str, txt: str) -> list[str]:
    t = clave(txt)
    return [k for tp, k, rx, no in REGLAS if tp == tipo and rx.search(t) and not (no and no.search(t))]


def tecnicas(txt: str, de_categoria: str) -> tuple[list[str], str]:
    """Una obra puede tener varias. Si tiene un subtipo, lleva también la técnica general,
    así el filtro "Encaje" incluye las de bolillos."""
    hallo = hallar("técnica", txt)
    # "tejido" a secas es lo menos preciso: si es lo único que dice el texto y la
    # sección del catálogo da una técnica (p. ej. Crochet), gana la sección
    if hallo == ["tejido"] and de_categoria:
        return [de_categoria], "c"
    if hallo:
        hallo += [GRUPO[k] for k in hallo if k in GRUPO]
        return [k for k in TEC if k in hallo], "o"
    if de_categoria:
        return [de_categoria], "c"
    return ["sin"], "n"


def materiales(txt: str, de_categoria: str) -> list[str]:
    hallo = hallar("material", txt) + ([de_categoria] if de_categoria else [])
    return [k for k in MAT if k in hallo]


def familias() -> pd.DataFrame:
    """`familias_categorias.csv` indexada por `categoria_id`."""
    return leer_csv(FAMILIAS).assign(categoria_id=lambda d: d.categoria_id.astype(int)).set_index("categoria_id")
