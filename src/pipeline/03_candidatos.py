"""Etapa 03 — Candidatos a duplicado de expositoras.

PASO 1 del flujo de deduplicación:

    03_candidatos.py   detecta pares candidatos            (este script)
    (a mano)           se anotan `Hecho` / `Comentarios`
    04_aplicar_dedup   ejecuta las decisiones, vía decisiones/fusiones_expositoras.csv

REPRODUCIBILIDAD — por qué lee la tabla *manual* y no la procesada
------------------------------------------------------------------
Este script leía `data/processed/tabla_normalizada.xlsx`, que es lo que escriben
`04b` y `04c`: dos etapas POSTERIORES. Eso cerraba un ciclo — la etapa 03 leía la
salida de la corrida anterior — y el resultado encogía en cada pasada: 519
expositoras daban 75 pares; una vez aplicadas las fusiones quedaban 471 expositoras
y 22 pares, y el archivo anotable se reescribía con menos filas que antes.

La línea de base correcta es `tabla_normalizada_manual.xlsx`: la tabla tal como la
mantiene la investigadora, ANTES de que el pipeline aplique ninguna decisión. Es la
misma base que usan `04_aplicar_dedup` y `audit_comentarios`. Como es fija, la
detección da siempre el mismo resultado, corras el pipeline las veces que corras.

El archivo de salida NUNCA pierde información:

  - arranca de la **semilla** `revision_duplicados.xlsx`, la revisión que hicieron a
    mano la investigadora y el estudiante (69 pares comentados). Así el archivo nace
    con todo el trabajo ya hecho en vez de nacer vacío, y se reconstruye solo aunque
    se borre;
  - las columnas `Hecho` y `Comentarios` anotadas a mano se conservan, emparejadas
    por `(id_A, id_B)`. Lo anotado en la propia salida tiene prioridad sobre la
    semilla, y `origen_comentario` dice de dónde viene cada uno;
  - los pares que ya figuraban en el archivo se mantienen aunque la detección de hoy
    no los proponga (columna `detectado`);
  - `ya_fusionada` marca los pares que `decisiones/fusiones_expositoras.csv` ya
    resolvió, para poder filtrarlos sin perderlos de vista.

Método de detección (determinístico, sin ajustes ad-hoc):

  1. Se normaliza cada nombre: minúsculas, sin tildes (unidecode), sin puntuación,
     espacios colapsados.
  2. Se calcula el ratio sobre el nombre completo y también sobre el "núcleo"
     (el nombre sin las partículas de/del/la/y/v/vda/viuda, que aparecen o no según
     la fuente: "Rosa V. de Lezcano" vs "Rosa V. Lescano").
  3. Es candidato si `token_sort_ratio` o `ratio` >= UMBRAL en cualquiera de las dos.
     `score` = el mayor de los ratios (0-100).
  4. También es candidato si los nombres son *compatibles* palabra por palabra
     (`compatibles()`, tipo "compatible"), aunque el ratio quede bajo UMBRAL. Cubre
     tres casos que el ratio sobre el nombre entero no ve (revisión 2026-10-11):
     inicial vs. nombre completo ("Simona P. de Castro" / "Simona Palacios de
     Castro"), una palabra de más ("Alfonsa de Barceló" / "Alfonsa Cuadrado de
     Barceló") y texto agregado tras un guion ("Mamerta Monteros -Escuela
     Sarmiento"). Pide nombre de pila parecido (>= 80), apellido parecido
     (>= UMBRAL_APELLIDO) y que las palabras del medio coincidan o sean la inicial
     de la otra, con a lo sumo una sobrante.

Entrada : data/interim/tabla_normalizada_manual.xlsx   (Expositoras, Ciudades, Objetos)
          data/interim/revision_duplicados.xlsx                     (semilla anotada)
          data/interim/decisiones/fusiones_expositoras.csv          (si existe)
          data/interim/duplicados_expositoras_candidatos.xlsx       (si existe: anotaciones)
Salida  : data/interim/duplicados_expositoras_candidatos.xlsx
"""
from __future__ import annotations

import csv
import re

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import DECISIONES, INTERIM

FUENTE = INTERIM / "tabla_normalizada_manual.xlsx"
SALIDA = INTERIM / "duplicados_expositoras_candidatos.xlsx"
FUSIONES_CSV = DECISIONES / "fusiones_expositoras.csv"
SEMILLA = INTERIM / "revision_duplicados.xlsx"
HOJA_SEMILLA = "Personas - candidatos"
HOJA = "candidatos"
UMBRAL = 87  # ratio mínimo (0-100) para proponer un par
UMBRAL_APELLIDO = 75  # en compatibles(): con 70 entraban Blanche/Sánchez, Pereira/Herrera

COLS = [
    "id_A", "nombre_A", "id_B", "nombre_B",
    "score", "tipo",
    "ciudades_A", "ciudades_B", "misma_ciudad",
    "concursos_A", "concursos_B", "n_obj_A", "n_obj_B",
    "id_objetos_A", "id_objetos_B",
    "ya_fusionada", "detectado",
    "Hecho", "Comentarios", "origen_comentario",
]

PARTICULAS = {"de", "del", "la", "las", "los", "y", "v", "vda", "viuda"}


def normaliza(s: str) -> str:
    s = unidecode(str(s)).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def nucleo(s: str) -> str:
    """Nombre normalizado sin las partículas (de/del/la/y/v/vda/viuda)."""
    return " ".join(t for t in normaliza(s).split() if t not in PARTICULAS)


def _palabras(s: str) -> list[str]:
    """Núcleo del nombre como lista, sin corchetes ni lo que va tras un guion
    ("Mamerta Monteros -Escuela Sarmiento" -> ["mamerta", "monteros"])."""
    s = re.sub(r"\[.*?\]", " ", str(s))
    s = re.split(r"\s-|-\s", s)[0]
    return nucleo(s).split()


def _palabra_ok(x: str, y: str) -> bool:
    if x == y:
        return True
    if len(x) == 1 or len(y) == 1:  # inicial: "p" vs "palacios"
        return x[0] == y[0]
    return fuzz.ratio(x, y) >= 80


def compatibles(a: str, b: str) -> bool:
    ta, tb = _palabras(a), _palabras(b)
    if len(ta) < 2 or len(tb) < 2:
        return False
    if len(ta[0]) == 1 and len(tb[0]) == 1 or not _palabra_ok(ta[0], tb[0]):
        return False
    ua, ub = ta[-1], tb[-1]
    if ua != ub and (len(ua) == 1 or len(ub) == 1 or fuzz.ratio(ua, ub) < UMBRAL_APELLIDO):
        return False
    medio_a, medio_b = ta[1:-1], tb[1:-1]
    if len(medio_a) > len(medio_b):
        medio_a, medio_b = medio_b, medio_a
    resto = list(medio_b)
    for t in medio_a:
        par = next((u for u in resto if _palabra_ok(t, u)), None)
        if par is None:
            return False
        resto.remove(par)
    return len(resto) <= 1


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
            compat = not (exacto or score >= UMBRAL) and compatibles(na, nb)
            if not (exacto or score >= UMBRAL or compat):
                continue
            if exacto:
                tipo = "exacto_norm"
            elif compat:
                tipo = "compatible (inicial / palabra agregada)"
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


def _txt(v) -> str:
    """Celda de Excel -> texto. Las vacías llegan como NaN y no deben escribirse."""
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)


def previas(ruta) -> dict[tuple[int, int], dict]:
    """Lee el archivo anterior: anotaciones a mano + pares ya listados.

    Nunca se pisan anotaciones ni se pierden pares (bitácora, 2026-09).
    """
    if not ruta.exists():
        return {}
    try:
        df = pd.read_excel(ruta)
    except Exception as e:  # archivo abierto en Excel, corrupto, etc.
        raise SystemExit(
            f"03_candidatos: no puedo leer {ruta.name} ({e.__class__.__name__}). "
            "Si lo tenés abierto en Excel, cerralo: el script conserva sus "
            "anotaciones y necesita leerlas antes de reescribirlo."
        )
    out = {}
    for r in df.to_dict("records"):
        try:
            clave = (int(r["id_A"]), int(r["id_B"]))
        except (KeyError, TypeError, ValueError):
            continue
        out[clave] = r
    return out


def semilla(ruta) -> dict[tuple[int, int], dict]:
    """Revisión anotada a mano (`revision_duplicados.xlsx`), como punto de partida."""
    if not ruta.exists():
        return {}
    df = pd.read_excel(ruta, sheet_name=HOJA_SEMILLA)
    out = {}
    for r in df.to_dict("records"):
        try:
            a, b = int(r["id_A"]), int(r["id_B"])
        except (KeyError, TypeError, ValueError):
            continue
        out[(min(a, b), max(a, b))] = r
    return out


def fusionados(ruta) -> set[tuple[int, int]]:
    """Pares ya resueltos por `decisiones/fusiones_expositoras.csv`."""
    if not ruta.exists():
        return set()
    pares = set()
    with ruta.open(encoding="utf-8", newline="") as fh:
        for fila in csv.DictReader(fh):
            grupo = [int(fila["mantener"])] + [int(x) for x in fila["descartar"].split()]
            for i, a in enumerate(grupo):
                for b in grupo[i + 1:]:
                    pares.add((min(a, b), max(a, b)))
    return pares


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E, C, O = xl.parse("Expositoras"), xl.parse("Ciudades"), xl.parse("Objetos")
    ctx = contexto(E, C, O)
    nombres = E.set_index("persona_id")["Nombre"].to_dict()

    anteriores = previas(SALIDA)
    sem = semilla(SEMILLA)
    ya = fusionados(FUSIONES_CSV)

    detectados = {(d["id_A"], d["id_B"]): d for d in detecta_pares(
        list(zip(E["persona_id"], E["Nombre"])))}

    filas = []
    for clave in sorted(set(detectados) | set(anteriores) | set(sem)):
        a, b = clave
        d = detectados.get(clave)
        prev = anteriores.get(clave, {})
        sm = sem.get(clave, {})
        # lo anotado en la propia salida manda; si está vacío, cae a la semilla
        hecho, coment = _txt(prev.get("Hecho")), _txt(prev.get("Comentarios"))
        # la procedencia es la ORIGINAL: si ya venia anotada, se conserva tal cual,
        # para que dos corridas seguidas den el mismo archivo.
        origen = _txt(prev.get("origen_comentario")) or ("candidatos" if coment else "")
        if not coment and _txt(sm.get("Comentarios")):
            hecho, coment = _txt(sm.get("Hecho")), _txt(sm.get("Comentarios"))
            origen = "revision_duplicados"
        elif not hecho:
            hecho = _txt(sm.get("Hecho"))
        ca, cb = ctx.get(a, {}), ctx.get(b, {})
        filas.append({
            "id_A": a,
            "nombre_A": (d or prev or sm).get("nombre_A") or nombres.get(a, ""),
            "id_B": b,
            "nombre_B": (d or prev or sm).get("nombre_B") or nombres.get(b, ""),
            "score": d["score"] if d else prev.get("score"),
            "tipo": d["tipo"] if d else prev.get("tipo"),
            "ciudades_A": ca.get("ciudades", ""), "ciudades_B": cb.get("ciudades", ""),
            "misma_ciudad": bool(ca.get("ciudades") and ca.get("ciudades") == cb.get("ciudades")),
            "concursos_A": ca.get("concursos", ""), "concursos_B": cb.get("concursos", ""),
            "n_obj_A": ca.get("n_obj"), "n_obj_B": cb.get("n_obj"),
            "id_objetos_A": ca.get("id_objetos", ""), "id_objetos_B": cb.get("id_objetos", ""),
            "ya_fusionada": clave in ya,
            "detectado": d is not None,
            # las anotaciones a mano mandan siempre
            "Hecho": hecho,
            "Comentarios": coment,
            "origen_comentario": origen,
        })

    df = pd.DataFrame(filas, columns=COLS)
    df = df.sort_values(
        by=["score", "id_A", "id_B"], ascending=[False, True, True], kind="stable",
    ).reset_index(drop=True)

    INTERIM.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=HOJA, index=False)

    nuevos = len(set(detectados) - set(anteriores))
    conservados = len(set(anteriores) - set(detectados))
    anotados = int((df["Comentarios"].astype(str).str.strip() != "").sum())
    print(f"{len(df)} pares en el archivo "
          f"({len(detectados)} detectados hoy, {nuevos} nuevos, "
          f"{conservados} conservados del archivo anterior)")
    print(f"  {int(df.ya_fusionada.sum())} ya resueltos en fusiones_expositoras.csv")
    desde_semilla = int((df["origen_comentario"] == "revision_duplicados").sum())
    print(f"  {anotados} con comentario anotado a mano "
          f"({desde_semilla} heredados de revision_duplicados.xlsx)")
    sin_revisar = int(((~df.ya_fusionada) &
                       (df["Comentarios"].astype(str).str.strip() == "")).sum())
    print(f"  {sin_revisar} sin fusionar y sin revisar  <-- lo que falta mirar")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()
