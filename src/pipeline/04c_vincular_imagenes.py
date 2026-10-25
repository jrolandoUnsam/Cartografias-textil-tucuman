"""Etapa 04c — Vincular cada objeto con la imagen escaneada de donde salió.

`data/interim/tabla_normalizada_manual.xlsx` tiene una hoja `Paginas_Catalogo`
(completada a mano) con, por cada imagen escaneada del catálogo, qué categoría y
qué rango de "N.º de órden" cubre esa página. Este script cruza eso contra la hoja
`Objetos` de `tabla_normalizada.xlsx` (concurso + categoría + si ORDEN cae en el
rango) y le agrega una columna `imagen`.

Solo cubre `fuente_id` 1 y 3 (los dos catálogos → Objetos). `fuente_id` 2 es el
fallo del jurado, que se corresponde con la hoja `Premios`, no con `Objetos`
(ver `04e_premios.py`) — queda fuera de este script.

La correspondencia por nombre no importa acá: usa `ORDEN` + `categoria_id` +
`concurso_id`, que no cambian con las fusiones de expositoras (`04_aplicar_dedup`)
ni con el paso a título de nombres (`04b_titulo_nombres`).

Además agrega `foto_album`: la foto del álbum de 1915 donde aparece el objeto, según
`decisiones/album_1915.csv` (transcripción de LM de cada foto; el `objeto_id` de cada
pieza lo encontramos cruzando n.º y descripción con el catálogo). Las fotos son las de
`data/raw/images/albumes/1915-album-version-2/`. Si un objeto aparece en varias, van
separadas por " | ".

Entrada : data/interim/tabla_normalizada_manual.xlsx (hoja Paginas_Catalogo)
          data/processed/tabla_normalizada.xlsx (hojas Objetos, Categorías)
          data/interim/decisiones/album_1915.csv
Salida  : data/processed/tabla_normalizada.xlsx, hoja Objetos con columnas `imagen` y
          `foto_album` agregadas (sobreescribe el archivo, respetando las demás hojas)
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

from _util import DECISIONES, INTERIM, PROCESSED

MANUAL = INTERIM / "tabla_normalizada_manual.xlsx"
ALBUM = DECISIONES / "album_1915.csv"
FUENTE = PROCESSED / "tabla_normalizada.xlsx"

# fuente_id de Paginas_Catalogo -> concurso_id de Objetos
CONCURSO_DE_FUENTE = {1: 1, 3: 2}


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def main() -> None:
    paginas = pd.ExcelFile(MANUAL).parse("Paginas_Catalogo")
    paginas = paginas[paginas["fuente_id"].isin(CONCURSO_DE_FUENTE)]
    paginas = paginas.dropna(subset=["orden_desde", "orden_hasta", "categoria_o_seccion"])

    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    O = hojas["Objetos"].copy()
    K = hojas[next(s for s in xl.sheet_names if s.startswith("Categor"))]
    cat_id_de_nombre = {norm(n): cid for cid, n in zip(K["categoria_id"], K["nombre_categoria"])}

    if "imagen" not in O.columns:
        O["imagen"] = pd.NA

    sin_match: set[str] = set()
    asignados = 0
    conflictos: list[tuple[int, str, str]] = []

    for _, fila in paginas.iterrows():
        concurso_id = CONCURSO_DE_FUENTE[int(fila["fuente_id"])]
        cat_key = norm(fila["categoria_o_seccion"])
        cat_id = cat_id_de_nombre.get(cat_key)
        if cat_id is None:
            sin_match.add(str(fila["categoria_o_seccion"]).strip())
            continue

        lo, hi = int(fila["orden_desde"]), int(fila["orden_hasta"])
        mask = (
            (O["concurso_id"] == concurso_id)
            & (O["categoria_id"] == cat_id)
            & (O["ORDEN"] >= lo)
            & (O["ORDEN"] <= hi)
        )
        for idx in O.index[mask]:
            previo = O.at[idx, "imagen"]
            if pd.notna(previo) and previo != fila["imagen"]:
                conflictos.append((int(O.at[idx, "objeto_id"]), previo, fila["imagen"]))
            O.at[idx, "imagen"] = fila["imagen"]
            asignados += 1

    album = pd.read_csv(ALBUM, dtype={"objeto_id": "Int64"}).dropna(subset=["objeto_id"])
    faltan = set(album["objeto_id"]) - set(O["objeto_id"])
    if faltan:
        raise ValueError(f"{ALBUM.name}: objeto_id {sorted(faltan)} no existe en Objetos")
    fotos = album.groupby("objeto_id")["foto"].agg(lambda s: " | ".join(dict.fromkeys(s)))
    O["foto_album"] = O["objeto_id"].map(fotos)
    hojas["Objetos"] = O

    with pd.ExcelWriter(FUENTE, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)

    total = len(O)
    con_imagen = O["imagen"].notna().sum()
    print(f"{asignados} asignaciones de rango aplicadas")
    print(f"{O['foto_album'].notna().sum()} objetos con foto del álbum de 1915")
    print(f"{con_imagen}/{total} objetos con imagen asignada "
          f"({total - con_imagen} sin página cargada todavía en Paginas_Catalogo)")
    if sin_match:
        print("\nCategorías de Paginas_Catalogo sin match en Categorías (se salteó su rango):")
        for c in sorted(sin_match):
            print(f"  - {c!r}")
    if conflictos:
        print(f"\n{len(conflictos)} objetos con rangos que se pisan entre sí "
              f"(quedó la última imagen escrita, revisar Paginas_Catalogo):")
        for objeto_id, antes, despues in conflictos[:10]:
            print(f"  objeto_id {objeto_id}: {antes!r} -> {despues!r}")
    print(f"\n-> {FUENTE}")


if __name__ == "__main__":
    main()
