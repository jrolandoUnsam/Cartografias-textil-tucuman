"""Etapa 03 — Candidatos a duplicado de expositoras.

PASO 1 del flujo de deduplicación:

    03_candidatos.py   detecta pares candidatos            (este script)
    (a mano)           se agregan pares extra + `Hecho` / `Comentarios`
    04_aplicar_dedup   ejecuta las decisiones anotadas

Este script NO usa ningún archivo anotado a mano: arranca de cero desde la hoja
`Expositoras` de `tabla_normalizada.xlsx` y propone, de forma reproducible, los
pares de nombres que *podrían* ser la misma persona. Solo compara nombres de
expositoras del catálogo (no toca la hoja Premios ni las ciudades).

Método (determinístico, sin ajustes ad-hoc):

  1. Se normaliza cada nombre: minúsculas, sin tildes (unidecode), sin puntuación,
     espacios colapsados.
  2. Se calcula el ratio sobre el nombre completo y también sobre el "núcleo"
     (el nombre sin las partículas de/del/la/y/v/vda/viuda, que aparecen o no según
     la fuente: "Rosa V. de Lezcano" vs "Rosa V. Lescano").
  3. Es candidato si `token_sort_ratio` o `ratio` >= UMBRAL en cualquiera de las dos.
     `score` = el mayor de los ratios (0-100).

Se agregan columnas de ayuda (ciudades y concursos de cada lado, si comparten
ciudad, nº de objetos y la lista de `objeto_id` de cada expositora) y dos columnas
vacías `Hecho` y `Comentarios` para anotar.

Entrada : data/processed/tabla_normalizada.xlsx   (Expositoras, Ciudades, Objetos)
Salida  : data/interim/duplicados_expositoras_candidatos.xlsx
"""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SALIDA = INTERIM / "duplicados_expositoras_candidatos.xlsx"
HOJA = "candidatos"
UMBRAL = 87  # ratio mínimo (0-100) para proponer un par

COLS = [
    "id_A", "nombre_A", "id_B", "nombre_B",
    "score", "tipo",
    "ciudades_A", "ciudades_B", "misma_ciudad",
    "concursos_A", "concursos_B", "n_obj_A", "n_obj_B",
    "id_objetos_A", "id_objetos_B",
    "Hecho", "Comentarios",
]

PARTICULAS = {"de", "del", "la", "las", "los", "y", "v", "vda", "viuda"}


def normaliza(s: str) -> str:
    s = unidecode(str(s)).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def nucleo(s: str) -> str:
    """Nombre normalizado sin las partículas (de/del/la/y/v/vda/viuda)."""
    return " ".join(t for t in normaliza(s).split() if t not in PARTICULAS)


def detecta_pares(items: list[tuple[int, str]]) -> list[dict]:
    """items = [(persona_id, nombre), ...]. Devuelve los pares candidatos."""
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
            lo, hi = (ida, idb) if ida < idb else (idb, ida)
            nlo, nhi = (na, nb) if ida < idb else (nb, na)
            out.append({"id_A": lo, "nombre_A": nlo, "id_B": hi, "nombre_B": nhi,
                        "score": 100.0 if exacto else round(score, 1), "tipo": tipo})
    out.sort(key=lambda d: (-d["score"], d["id_A"], d["id_B"]))
    return out


def contexto(E: pd.DataFrame, C: pd.DataFrame, O: pd.DataFrame) -> dict[int, dict]:
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
            "id_objetos": ", ".join(str(o) for o in sorted(sub["objeto_id"])),
        }
    return ctx


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E, C, O = xl.parse("Expositoras"), xl.parse("Ciudades"), xl.parse("Objetos")
    ctx = contexto(E, C, O)

    filas = []
    for d in detecta_pares(list(zip(E["persona_id"], E["Nombre"]))):
        ca, cb = ctx.get(d["id_A"], {}), ctx.get(d["id_B"], {})
        filas.append({
            **d,
            "ciudades_A": ca.get("ciudades", ""), "ciudades_B": cb.get("ciudades", ""),
            "misma_ciudad": bool(ca.get("ciudades") and ca.get("ciudades") == cb.get("ciudades")),
            "concursos_A": ca.get("concursos", ""), "concursos_B": cb.get("concursos", ""),
            "n_obj_A": ca.get("n_obj"), "n_obj_B": cb.get("n_obj"),
            "id_objetos_A": ca.get("id_objetos", ""), "id_objetos_B": cb.get("id_objetos", ""),
            "Hecho": "", "Comentarios": "",
        })
    df = pd.DataFrame(filas, columns=COLS)

    INTERIM.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=HOJA, index=False)

    print(f"{len(df)} pares candidatos "
          f"(exacto_norm: {(df.tipo == 'exacto_norm').sum()}, "
          f"alta: {(df.tipo == 'alta').sum()}, "
          f"media: {(df.tipo.str.startswith('media')).sum()})")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()
