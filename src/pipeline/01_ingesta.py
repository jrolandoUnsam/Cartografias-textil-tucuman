"""Etapa 01 — Ingesta.

Lee las hojas de catálogo del Excel crudo y las convierte en una tabla larga
(un registro por objeto), separando las filas 'explotadas' de 1916.

Entrada : data/raw/TUCUMÁN text 1915-16 DATOS.xlsx
Salida  : data/interim/objetos_crudos.csv

Las hojas 'no PRENSA-EL ORDEN', 'no ARCHIVO PADILLA' y 'no Prensa-Rakow lib' NO se
procesan (material de contexto).
"""
from __future__ import annotations

import pandas as pd

from _util import DECISIONES, INTERIM, RAW_XLSX, limpiar_texto, separar_orden_objeto

OVERRIDE = DECISIONES / "objetos_texto_override.csv"

COLS = ["fuente", "concurso_id", "nombre_raw", "ciudad_raw", "categoria_raw", "orden", "objeto"]


def _norm(x) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return limpiar_texto(str(x))


def ingesta_1915(xls: pd.ExcelFile) -> pd.DataFrame:
    hoja = "1915 1er concurso EXPOS"
    df = xls.parse(hoja, header=None)
    inicio = df.index[df[0].astype(str).str.strip() == "NOMBRE"][0] + 1
    filas = []
    for _, r in df.loc[inicio:].iterrows():
        nombre = _norm(r[0])
        if not nombre:
            continue
        filas.append({
            "fuente": hoja,
            "concurso_id": 1,
            "nombre_raw": nombre,
            "ciudad_raw": _norm(r[1]),
            "categoria_raw": _norm(r[2]),
            "orden": _norm(r[4]),
            "objeto": _norm(r[3]),
        })
    return pd.DataFrame(filas, columns=COLS)


def ingesta_1916(xls: pd.ExcelFile) -> pd.DataFrame:
    hoja = "1916 Concurso Tejidos"
    df = xls.parse(hoja, header=None)
    filas = []
    for _, r in df.iterrows():
        if _norm(r[0]) != "1916":
            continue
        nombre = _norm(r[1])
        ciudad = _norm(r[2])
        categoria = _norm(r[5])
        for orden, objeto in separar_orden_objeto(_norm(r[3]), _norm(r[4])):
            filas.append({
                "fuente": hoja,
                "concurso_id": 2,
                "nombre_raw": nombre,
                "ciudad_raw": ciudad,
                "categoria_raw": categoria,
                "orden": "" if orden is None else str(orden),
                "objeto": objeto,
            })
    return pd.DataFrame(filas, columns=COLS)


def main() -> None:
    xls = pd.ExcelFile(RAW_XLSX)
    out = pd.concat([ingesta_1915(xls), ingesta_1916(xls)], ignore_index=True)
    out.insert(0, "objeto_id", range(1, len(out) + 1))

    # Correcciones manuales de texto: celdas que la investigadora editó a mano
    # respecto del catálogo (erratas de orden, singular/plural, mayúsculas).
    if OVERRIDE.exists():
        ov = pd.read_csv(OVERRIDE, dtype=str).set_index("objeto_id")
        for col in ("objeto", "orden"):
            if col in ov.columns:
                mapa = ov[col].dropna().to_dict()
                out[col] = out.apply(
                    lambda r: mapa.get(str(r["objeto_id"]), r[col]), axis=1
                )
        print(f"aplicadas {len(ov)} correcciones (objetos_texto_override.csv)")

    INTERIM.mkdir(parents=True, exist_ok=True)
    destino = INTERIM / "objetos_crudos.csv"
    out.to_csv(destino, index=False, encoding="utf-8")
    print(f"{len(out)} objetos -> {destino}")
    print(out.groupby("fuente").size().to_string())


if __name__ == "__main__":
    main()
