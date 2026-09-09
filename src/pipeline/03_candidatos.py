"""Etapa 03 — Candidatos a duplicado (personas y ciudades).

PASO 1 del flujo de deduplicación:

    03_candidatos.py   detecta pares candidatos           (este script)
    (a mano)           se anotan `Hecho` y `Comentarios`
    04_aplicar_dedup   ejecuta las decisiones anotadas

Cómo arma la lista de candidatos:

  1. SEMILLA: parte del archivo revisado a mano `data/interim/revision_duplicados.xlsx`.
     Todos sus pares se conservan tal cual, con sus `Hecho` / `Comentarios`, aunque
     el método automático ya no los proponga (p. ej. porque una de las dos filas ya
     se fusionó, o porque son un par que se agregó a criterio humano).

  2. DETECCIÓN automática, una función por entidad
     (`duplicados_expositoras`, `duplicados_ciudades`). Método determinístico:
       - se normaliza el nombre (minúsculas, sin tildes, sin puntuación)
       - se compara el nombre completo y también el "núcleo" (sin las partículas
         de/del/la/y/v/vda/viuda, que aparecen o no según la fuente)
       - es candidato si `token_sort_ratio` o `ratio` >= UMBRAL en cualquiera de las dos
     Los pares detectados que NO están en la semilla se agregan como `origen = nuevo`.

  3. Se agregan columnas de ayuda (score, tipo, ciudades y concursos de cada lado,
     nº de objetos, si comparten ciudad).

Entrada : data/processed/tabla_normalizada.xlsx   (Expositoras, Ciudades, Objetos)
          data/interim/revision_duplicados.xlsx    (semilla anotada a mano)
Salida  : data/interim/revision_duplicados_regenerado.xlsx   (archivo NUEVO; la
          semilla no se toca)

Al final imprime la comparación semilla ↔ detección:
  - pares de la semilla que el método NO vuelve a proponer (y por qué)
  - pares nuevos que propone el método y no estaban en la semilla
"""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SEMILLA = INTERIM / "revision_duplicados.xlsx"
SALIDA = INTERIM / "revision_duplicados_regenerado.xlsx"
UMBRAL = 87  # ratio mínimo (0-100) para proponer un par

HOJA_P = "Personas - candidatos"
HOJA_C = "Ciudades - candidatos"

COLS = [
    "id_A", "nombre_A", "id_B", "nombre_B",
    "Hecho", "Comentarios",
    "origen", "detectado", "score", "tipo",
    "ciudades_A", "ciudades_B", "misma_ciudad",
    "concursos_A", "concursos_B", "n_obj_A", "n_obj_B",
]

PARTICULAS = {"de", "del", "la", "las", "los", "y", "v", "vda", "viuda"}


# --------------------------------------------------------------------------- #
# normalización + comparación
# --------------------------------------------------------------------------- #
def normaliza(s: str) -> str:
    s = unidecode(str(s)).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def nucleo(s: str) -> str:
    """Nombre normalizado sin las partículas (de/del/la/y/v/vda/viuda)."""
    return " ".join(t for t in normaliza(s).split() if t not in PARTICULAS)


def _pares(items: list[tuple[int, str]]) -> list[dict]:
    """items = [(id, nombre), ...]. Devuelve los pares candidatos con score y tipo."""
    items = [(i, n) for i, n in items if str(n).strip() and str(n).strip().lower() != "nan"]
    norm = {i: normaliza(n) for i, n in items}
    nuc = {i: nucleo(n) for i, n in items}
    out = []
    for a in range(len(items)):
        ida, na = items[a]
        for b in range(a + 1, len(items)):
            idb, nb = items[b]
            xa, xb = norm[ida], norm[idb]
            if not xa or not xb:
                continue
            exacto = xa == xb
            score_full = max(fuzz.token_sort_ratio(xa, xb), fuzz.ratio(xa, xb))
            ca, cb = nuc[ida], nuc[idb]
            score_nuc = max(fuzz.token_sort_ratio(ca, cb), fuzz.ratio(ca, cb)) if ca and cb else 0.0
            score = max(score_full, score_nuc)
            if not (exacto or score >= UMBRAL):
                continue
            if exacto:
                tipo = "exacto_norm"
            elif score_full < UMBRAL <= score_nuc:
                tipo = "media (sin partículas)"
            else:
                tipo = "alta" if score >= 93 else "media"
            lo, hi = sorted((ida, idb))
            out.append({"id_A": lo, "id_B": hi,
                        "score": 100.0 if exacto else round(score, 1), "tipo": tipo})
    return out


def duplicados_expositoras(E: pd.DataFrame) -> list[dict]:
    return _pares(list(zip(E["persona_id"], E["Nombre"])))


def duplicados_ciudades(C: pd.DataFrame) -> list[dict]:
    return _pares(list(zip(C["ciudad_id"], C["nombre_ciudad"])))


# --------------------------------------------------------------------------- #
# contexto de ayuda
# --------------------------------------------------------------------------- #
def contexto_personas(E: pd.DataFrame, C: pd.DataFrame, O: pd.DataFrame) -> dict[int, dict]:
    ciu = C.set_index("ciudad_id")["nombre_ciudad"].to_dict()
    anio = {1: "1915", 2: "1916"}
    ctx: dict[int, dict] = {}
    for pid in E["persona_id"]:
        sub = O[O["expositora_id"] == pid]
        ctx[pid] = {
            "ciudades": ", ".join(sorted({str(ciu.get(c)) for c in sub["ciudad_id"]
                                          if pd.notna(ciu.get(c))})),
            "concursos": ", ".join(sorted({anio.get(c, str(c)) for c in sub["concurso_id"]})),
            "n_obj": len(sub),
        }
    return ctx


def contexto_ciudades(C: pd.DataFrame, O: pd.DataFrame) -> dict[int, dict]:
    prov = C.set_index("ciudad_id")["nombre_provincia"].to_dict()
    n = O.groupby("ciudad_id").size().to_dict()
    return {cid: {"ciudades": str(prov.get(cid, "")), "concursos": "",
                  "n_obj": int(n.get(cid, 0))} for cid in C["ciudad_id"]}


# --------------------------------------------------------------------------- #
# armado de la hoja
# --------------------------------------------------------------------------- #
def _nombre(idx: int, E_nom: dict, semilla_nom: dict) -> str:
    """Nombre actual de la entidad; si ya no existe, el que quedó registrado en la semilla."""
    if idx in E_nom and pd.notna(E_nom[idx]):
        return str(E_nom[idx])
    return semilla_nom.get(idx, "—")


def construye_hoja(detectados: list[dict], semilla: pd.DataFrame,
                   nombres: dict, ctx: dict) -> pd.DataFrame:
    col_com = "Comentarios" if "Comentarios" in semilla.columns else "Comendatios"
    # nombres tal como quedaron registrados en la semilla (por si el id ya no existe)
    sem_nom: dict[int, str] = {}
    sem_anot: dict[tuple, tuple] = {}
    for _, r in semilla.iterrows():
        a, b = int(r["id_A"]), int(r["id_B"])
        sem_nom.setdefault(a, str(r["nombre_A"]))
        sem_nom.setdefault(b, str(r["nombre_B"]))
        sem_anot[(a, b)] = (r.get("Hecho"), r.get(col_com))

    det = {(d["id_A"], d["id_B"]): d for d in detectados}
    claves = list(sem_anot) + [k for k in det if k not in sem_anot]

    filas = []
    for k in claves:
        a, b = k
        d = det.get(k, {})
        en_sem = k in sem_anot
        origen = "semilla+detectado" if (en_sem and k in det) else ("semilla" if en_sem else "nuevo")
        ca, cb = ctx.get(a, {}), ctx.get(b, {})
        filas.append({
            "id_A": a, "nombre_A": _nombre(a, nombres, sem_nom),
            "id_B": b, "nombre_B": _nombre(b, nombres, sem_nom),
            "Hecho": sem_anot.get(k, (None, None))[0],
            "Comentarios": sem_anot.get(k, (None, None))[1],
            "origen": origen,
            "detectado": "sí" if k in det else "no",
            "score": d.get("score"),
            "tipo": d.get("tipo"),
            "ciudades_A": ca.get("ciudades", ""), "ciudades_B": cb.get("ciudades", ""),
            "misma_ciudad": bool(ca.get("ciudades") and ca.get("ciudades") == cb.get("ciudades")),
            "concursos_A": ca.get("concursos", ""), "concursos_B": cb.get("concursos", ""),
            "n_obj_A": ca.get("n_obj"), "n_obj_B": cb.get("n_obj"),
        })
    df = pd.DataFrame(filas, columns=COLS)
    for c in ("concursos_A", "concursos_B"):
        df[c] = df[c].fillna("").astype(str)
    df["Hecho"] = df["Hecho"].map(lambda v: "" if pd.isna(v) else bool(v))
    df["_o"] = df["origen"].map({"nuevo": 0, "semilla+detectado": 1, "semilla": 2})
    return df.sort_values(["_o", "score", "id_A", "id_B"],
                          ascending=[True, False, True, True]).drop(columns="_o").reset_index(drop=True)


def compara(df: pd.DataFrame, etiqueta: str, vivos: set[int]) -> None:
    falta = df[(df["origen"] == "semilla") & (df["detectado"] == "no")]
    nuevo = df[df["origen"] == "nuevo"]
    print(f"\n=== {etiqueta} ===")
    print(f"  total {len(df)}  |  en semilla {(df.origen != 'nuevo').sum()}  "
          f"|  detección propone {(df.detectado == 'sí').sum()}")
    print(f"  -- {len(falta)} pares de la semilla que la detección NO vuelve a proponer:")
    for _, r in falta.iterrows():
        if r.id_A not in vivos or r.id_B not in vivos:
            motivo = "ya fusionado: uno de los dos ids no existe en la tabla"
        else:
            motivo = "nombres poco parecidos (par agregado a criterio humano)"
        print(f"       {r.id_A} {r.nombre_A!r} <> {r.id_B} {r.nombre_B!r}  · {motivo}")
    print(f"  -- {len(nuevo)} pares NUEVOS que propone la detección:")
    for _, r in nuevo.iterrows():
        print(f"       {r.id_A} {r.nombre_A!r} <> {r.id_B} {r.nombre_B!r}  "
              f"(score {r.score}, {r.tipo})")


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E, C, O = xl.parse("Expositoras"), xl.parse("Ciudades"), xl.parse("Objetos")
    sp = pd.read_excel(SEMILLA, sheet_name=HOJA_P)
    sc = pd.read_excel(SEMILLA, sheet_name=HOJA_C)

    personas = construye_hoja(
        duplicados_expositoras(E), sp,
        E.set_index("persona_id")["Nombre"].to_dict(),
        contexto_personas(E, C, O))
    ciudades = construye_hoja(
        duplicados_ciudades(C), sc,
        C.set_index("ciudad_id")["nombre_ciudad"].to_dict(),
        contexto_ciudades(C, O))

    INTERIM.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        personas.to_excel(w, sheet_name=HOJA_P, index=False)
        ciudades.to_excel(w, sheet_name=HOJA_C, index=False)

    compara(personas, "Personas", set(E["persona_id"]))
    compara(ciudades, "Ciudades", set(C["ciudad_id"]))
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
