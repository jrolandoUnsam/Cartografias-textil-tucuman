"""Etapa 03 — Candidatos a duplicado (personas y ciudades).

Genera, de forma reproducible, los pares de expositoras y de ciudades que *podrían*
ser la misma entidad, para que se revisen a mano. NO decide nada: solo propone.

Método (determinístico, sin ajustes ad-hoc):
  1. Se normaliza cada nombre: minúsculas, sin tildes (unidecode), sin puntuación,
     espacios colapsados.
  2. Se calcula el ratio sobre el nombre normalizado y también sobre el "núcleo"
     (el nombre sin las partículas de/del/la/y/v/vda/viuda, que suelen aparecer o
     no según la fuente: "Rosa V. de Lezcano" vs "ROSA V. LESCANO").
  3. Un par es candidato si:
       - los nombres normalizados son idénticos           -> tipo "exacto_norm"
       - o  token_sort_ratio / ratio  >= UMBRAL  (nombre completo)
       - o  token_sort_ratio / ratio  >= UMBRAL  (núcleo, sin partículas)
     `score` = el mayor de los ratios (0-100); `tipo` indica si lo trajo el núcleo.
  3. Se agregan columnas de contexto (ciudades / provincia / nº de objetos de cada
     lado) para ayudar a decidir.

Entrada  : data/processed/tabla_normalizada.xlsx  (hojas Expositoras, Ciudades, Objetos)
Salida   : data/interim/revision_duplicados.xlsx  (hojas 'Personas - candidatos',
           'Ciudades - candidatos')

NO destructivo: si el archivo de salida ya existe, se conservan las columnas
`Hecho` y `Comentarios` de cada par ya revisado (emparejando por el par de ids, sin
importar el orden). Los pares nuevos se agregan con esas columnas vacías. Ningún par
ya anotado se pierde, aunque el método deje de proponerlo.
"""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SALIDA = INTERIM / "revision_duplicados.xlsx"
UMBRAL = 87  # ratio mínimo (0-100) para proponer un par

COLS_SALIDA = [
    "id_A", "nombre_A", "id_B", "nombre_B",
    "score", "tipo", "ctx_A", "ctx_B", "n_obj_A", "n_obj_B",
    "origen", "Hecho", "Comentarios",
]


PARTICULAS = {"de", "del", "la", "las", "los", "y", "v", "vda", "viuda"}


def normaliza(s: str) -> str:
    s = unidecode(str(s)).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def nucleo(s: str) -> str:
    """Nombre normalizado sin las partículas (de/del/la/y/v/vda/viuda)."""
    return " ".join(t for t in normaliza(s).split() if t not in PARTICULAS)


def pares_candidatos(items: list[tuple[int, str]]) -> list[dict]:
    """items = [(id, nombre), ...] ya ordenados por id ascendente.

    Se ignoran los registros sin nombre (p. ej. ciudades que solo tienen provincia).
    """
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
            out.append({
                "id_A": ida, "nombre_A": na, "id_B": idb, "nombre_B": nb,
                "score": 100.0 if exacto else round(score, 1),
                "tipo": tipo,
            })
    out.sort(key=lambda d: (-d["score"], d["id_A"], d["id_B"]))
    return out


def contexto_personas(O: pd.DataFrame, C: pd.DataFrame) -> dict[int, tuple[str, int]]:
    ciu = C.set_index("ciudad_id")["nombre_ciudad"].to_dict()
    g = O.groupby("expositora_id")
    ctx = {}
    for pid, sub in g:
        cs = sorted({str(ciu.get(c, "")) for c in sub["ciudad_id"] if pd.notna(ciu.get(c))})
        ctx[pid] = (", ".join(x for x in cs if x), len(sub))
    return ctx


def contexto_ciudades(O: pd.DataFrame, C: pd.DataFrame) -> dict[int, tuple[str, int]]:
    prov = C.set_index("ciudad_id")["nombre_provincia"].to_dict()
    n = O.groupby("ciudad_id").size().to_dict()
    return {cid: (str(prov.get(cid, "")), int(n.get(cid, 0))) for cid in C["ciudad_id"]}


def fusiona_anotaciones(nuevos: pd.DataFrame, hoja: str) -> pd.DataFrame:
    """Conserva Hecho/Comentarios de la revisión previa y no pierde pares anotados."""
    prev = None
    if SALIDA.exists():
        try:
            prev = pd.read_excel(SALIDA, sheet_name=hoja)
        except ValueError:
            prev = None

    def clave(a, b):
        return tuple(sorted((int(a), int(b))))

    anot = {}
    if prev is not None:
        col_com = "Comentarios" if "Comentarios" in prev.columns else (
            "Comendatios" if "Comendatios" in prev.columns else None)
        for _, r in prev.iterrows():
            k = clave(r["id_A"], r["id_B"])
            anot[k] = (r.get("Hecho"), r.get(col_com) if col_com else None)

    nuevos = nuevos.copy()
    nuevos["origen"] = "nuevo"
    nuevos["Hecho"] = None
    nuevos["Comentarios"] = None
    vistos = set()
    for idx, r in nuevos.iterrows():
        k = clave(r["id_A"], r["id_B"])
        vistos.add(k)
        if k in anot:
            nuevos.at[idx, "Hecho"] = anot[k][0]
            nuevos.at[idx, "Comentarios"] = anot[k][1]
            nuevos.at[idx, "origen"] = "revisado"

    # pares anotados antes que el método ya no propone: se conservan igual
    extra = []
    if prev is not None:
        for _, r in prev.iterrows():
            k = clave(r["id_A"], r["id_B"])
            if k in vistos:
                continue
            col_com = "Comentarios" if "Comentarios" in prev.columns else "Comendatios"
            extra.append({
                "id_A": k[0], "nombre_A": r["nombre_A"] if r["id_A"] == k[0] else r["nombre_B"],
                "id_B": k[1], "nombre_B": r["nombre_B"] if r["id_B"] == k[1] else r["nombre_A"],
                "score": None, "tipo": "solo_revision_previa",
                "ctx_A": None, "ctx_B": None, "n_obj_A": None, "n_obj_B": None,
                "origen": "solo_previo",
                "Hecho": r.get("Hecho"), "Comentarios": r.get(col_com, None),
            })
    filas = nuevos.reindex(columns=COLS_SALIDA).to_dict("records") + [
        {c: e.get(c) for c in COLS_SALIDA} for e in extra
    ]
    return pd.DataFrame(filas, columns=COLS_SALIDA)


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E = xl.parse("Expositoras")
    C = xl.parse("Ciudades")
    O = xl.parse("Objetos")

    ctx_p = contexto_personas(O, C)
    cand_p = pd.DataFrame(pares_candidatos(list(zip(E["persona_id"], E["Nombre"]))))
    cand_p["ctx_A"] = cand_p["id_A"].map(lambda i: ctx_p.get(i, ("", 0))[0])
    cand_p["ctx_B"] = cand_p["id_B"].map(lambda i: ctx_p.get(i, ("", 0))[0])
    cand_p["n_obj_A"] = cand_p["id_A"].map(lambda i: ctx_p.get(i, ("", 0))[1])
    cand_p["n_obj_B"] = cand_p["id_B"].map(lambda i: ctx_p.get(i, ("", 0))[1])

    ctx_c = contexto_ciudades(O, C)
    cand_c = pd.DataFrame(pares_candidatos(list(zip(C["ciudad_id"], C["nombre_ciudad"]))))
    if len(cand_c):
        cand_c["ctx_A"] = cand_c["id_A"].map(lambda i: ctx_c.get(i, ("", 0))[0])
        cand_c["ctx_B"] = cand_c["id_B"].map(lambda i: ctx_c.get(i, ("", 0))[0])
        cand_c["n_obj_A"] = cand_c["id_A"].map(lambda i: ctx_c.get(i, ("", 0))[1])
        cand_c["n_obj_B"] = cand_c["id_B"].map(lambda i: ctx_c.get(i, ("", 0))[1])

    personas = fusiona_anotaciones(cand_p, "Personas - candidatos")
    ciudades = fusiona_anotaciones(cand_c, "Ciudades - candidatos")

    INTERIM.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        personas.to_excel(w, sheet_name="Personas - candidatos", index=False)
        ciudades.to_excel(w, sheet_name="Ciudades - candidatos", index=False)

    def resumen(df, etiqueta):
        n = len(df)
        rev = (df["origen"] == "revisado").sum()
        nue = (df["origen"] == "nuevo").sum()
        prevonly = (df["origen"] == "solo_previo").sum()
        print(f"{etiqueta}: {n} pares  ({nue} nuevos sin revisar, {rev} ya revisados, "
              f"{prevonly} solo de la revisión previa)")

    resumen(personas, "Personas")
    resumen(ciudades, "Ciudades")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()
