"""Etapa 04 — Aplicar las fusiones de expositoras duplicadas.

PASO 3 del flujo de deduplicación:

    03_candidatos.py    detecta pares candidatos
    (a mano)            se anota Hecho / Comentarios en duplicados_expositoras_candidatos.xlsx
    04_aplicar_dedup.py ejecuta las decisiones anotadas          (este script)

Cada decisión es una fila de `data/interim/decisiones/fusiones_expositoras.csv`:
para cada id de `descartar`, mueve sus objetos (`Objetos.expositora_id`) al id
`mantener` y borra esa fila de `Expositoras`. Queda una sola persona por decisión,
con todos sus objetos juntos. Los premios de la hoja `Premios` que apuntaban a un id
descartado pasan a apuntar al id que queda (`persona_id` y `persona`).

La columna `origen` dice de dónde sale la decisión:

  decidida  el comentario de la revisión dice explícitamente qué lado se conserva.
  sin_lado  el comentario dice "unificar" sin aclarar qué id queda. Como el nombre
            ya quedó idéntico en los dos lados, el número no cambia el resultado
            visible; sí cambia cuántos objetos hay que mover. Criterio aplicado:
            conservar el lado con más objetos (menos movimientos).
  cluster   grupo de 3+ ids resuelto como una sola decisión, no par por par.

Entrada : data/interim/tabla_normalizada_manual.xlsx   (export manual más reciente,
          con las revisiones de Larisa en la hoja Premios)
          data/interim/decisiones/fusiones_expositoras.csv
Salida  : data/interim/tabla_normalizada_dedup.xlsx   (insumo de 04b)
"""
from __future__ import annotations

import csv
from dataclasses import dataclass

import pandas as pd

from _util import DECISIONES, INTERIM

FUENTE = INTERIM / "tabla_normalizada_manual.xlsx"
SALIDA = INTERIM / "tabla_normalizada_dedup.xlsx"
FUSIONES_CSV = DECISIONES / "fusiones_expositoras.csv"


@dataclass
class Fusion:
    mantener: int
    descartar: list[int]
    origen: str = ""
    nota: str = ""


def leer_fusiones(ruta=FUSIONES_CSV) -> list[Fusion]:
    with ruta.open(encoding="utf-8", newline="") as fh:
        return [
            Fusion(
                mantener=int(r["mantener"]),
                descartar=[int(x) for x in r["descartar"].split()],
                origen=r.get("origen", ""),
                nota=r.get("nota", ""),
            )
            for r in csv.DictReader(fh)
        ]


def aplicar(E: pd.DataFrame, O: pd.DataFrame, fusiones: list[Fusion]):
    E, O = E.copy(), O.copy()
    log = []
    for f in fusiones:
        movidos = []
        for d in f.descartar:
            n = int((O["expositora_id"] == d).sum())
            O.loc[O["expositora_id"] == d, "expositora_id"] = f.mantener
            movidos.append((d, n))
        E = E[~E["persona_id"].isin(f.descartar)]
        log.append((f.mantener, movidos, f.nota))
    return E, O, log


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    E, O = hojas["Expositoras"], hojas["Objetos"]
    ids = set(E["persona_id"])

    validas = []
    for f in leer_fusiones():
        if f.mantener not in ids:
            print(f"AVISO — se omite entera (el id a conservar {f.mantener} ya no "
                  f"existe en {FUENTE.name}): {f.nota}")
            continue
        for d in f.descartar:
            if d not in ids:
                print(f"AVISO — {f.nota}: el id {d} ya no existe en "
                      f"{FUENTE.name}, se ignora")
        vivos = [d for d in f.descartar if d in ids]
        if vivos:
            validas.append(Fusion(f.mantener, vivos, f.origen, f.nota))

    E2, O2, log = aplicar(E, O, validas)

    # La hoja Premios también apunta a expositoras: si no se reapunta, un premio
    # queda colgado de un id que la fusión acaba de borrar.
    if "Premios" in hojas and "persona_id" in hojas["Premios"].columns:
        P = hojas["Premios"].copy()
        destino = {d: f.mantener for f in validas for d in f.descartar}
        nombre = E2.set_index("persona_id")["Nombre"]
        afectadas = P["persona_id"].isin(list(destino))
        for idx in P.index[afectadas]:
            viejo = int(P.at[idx, "persona_id"])
            P.at[idx, "persona_id"] = destino[viejo]
            if "persona" in P.columns:
                P.at[idx, "persona"] = nombre[destino[viejo]]
            print(f"  Premios fila {idx}: persona_id {viejo} -> {destino[viejo]}")
        hojas["Premios"] = P

    print(f"\n{len(log)} fusiones aplicadas · "
          f"{len(E) - len(E2)} filas de Expositoras eliminadas")
    for mantener, movidos, nota in log:
        detalle = ", ".join(f"{n} obj. de {d}" for d, n in movidos)
        print(f"  -> queda {mantener}: {nota}  [{detalle}]")

    # sanity check: ids duplicados / objetos huérfanos
    assert E2["persona_id"].is_unique, "quedaron ids de expositora duplicados"
    assert set(O2["expositora_id"]) <= set(E2["persona_id"]), "quedaron objetos huérfanos"

    hojas["Expositoras"], hojas["Objetos"] = E2, O2
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
