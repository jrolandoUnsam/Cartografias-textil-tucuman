"""Etapa 03b — Vincular cada línea de la hoja `Premios` con la hoja `Objetos`.

Toma la hoja `Premios` de `tabla_normalizada.xlsx` (fallo del jurado de 1915) y le
agrega, fila por fila y en el mismo orden, dos columnas:

    persona_id   ->  Expositoras.persona_id  (por nombre)
    objeto_id    ->  Objetos.objeto_id       (por categoría + N.º de orden,
                                              CONFIRMADO por nombre del dueño real)

Salida: data/interim/premios_vinculados.xlsx

Diferencia con la versión anterior (`git log` / `docs/bitacora.md` 2026-09-14): cruzaba por
categoría + N.º de orden y, si quedaba un único objeto candidato, lo tomaba sin
chequear si el nombre del dueño real tenía algo que ver con el nombre del premio
—la comparación de persona solo se usaba, antes, para desempatar cuando había MÁS
de un candidato, y ni así se verificaba el resultado final—. Eso dejaba premios
vinculados al objeto de otra persona (ver bitácora: filas 60, 61, 99).

Esta versión agrega un paso más al final: una vez resuelto el/los `objeto_id`
candidato(s) por categoría + orden, compara el nombre del premio contra el nombre
de quien realmente figura como dueño de ese objeto en `Objetos` (matching
aproximado, igual criterio que para personas). Si no se parecen lo suficiente
(`UMBRAL_NOMBRE`), el vínculo se descarta y la fila queda para revisar a mano —el
candidato descartado se deja anotado en `candidato_rechazado` para no perder el
dato.

Columnas agregadas:
    persona_id, persona            expositora resuelta y su nombre normalizado
    persona_score                  0-100; < 90 = revisar
    objeto_id                      id del objeto; varios ids separados por ";" si el
                                   premio abarca un rango ("17, 18, 19, 20 y 21")
    objeto_match                   cómo se resolvió, o el motivo si quedó vacío
    candidato_rechazado            objeto que se hubiera puesto sin el chequeo de
                                   nombre, y de quién es en realidad (solo si se
                                   rechazó algo)
    revisar                        X si hay que mirarlo a mano

Correcciones a mano: data/interim/decisiones/premios_manual.csv
    premio_id,objeto_id,persona_id,nota
    (premio_id = número de fila 0-based de la hoja Premios; objeto_id="ninguno"
    fuerza a que quede sin objeto sin correr el cruce automático)
"""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import DECISIONES, INTERIM, PROCESSED

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SALIDA = INTERIM / "premios_vinculados.xlsx"
MANUAL = DECISIONES / "premios_manual.csv"
UMBRAL_NOMBRE = 60  # 0-100, mismo umbral que ya usaba el desempate por texto

# CATEGORÍA del fallo -> categoría(s) del catálogo 1915.
CROSSWALK = {
    "FRAZADA DE LANA": ["COLCHAS Y FRAZADAS"],
    "FRAZADA DE ALGODÓN": ["COLCHAS Y FRAZADAS"],
    "ALFOMBRA": ["ALFOMBRAS"],
    "PONCHO DE LANA": ["PONCHOS"],
    "PONCHO DE HILO": ["PONCHOS"],
    "RANDA": ["RANDAS"],
    "encaje": ["ENCAJES VARIOS"],
    "DESHILADO": ["DESHILADO"],
    "BORDADO EN BLANCO Y SEDA": ["BORDADO EN BLANCO Y SEDA"],
    "CROCHET E IRLANDA": ["CROCHET"],
    "Raffia": ["RAFFIA IMITACIÓN CON HOJAS DE CAÑA"],
    "Jergón": ["PELLONES Y JERGONES"],
    "SENDERO": ["TEJIDOS VARIOS"],
    "ALFORJA": ["TEJIDOS VARIOS"],
    "MANTEL DE ALGODÓN": ["TEJIDOS VARIOS"],
}


def norm(s) -> str:
    s = unidecode(str(s)).lower().strip()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def parse_num(v) -> list[int]:
    s = str(v).strip().lower()
    if s in ("", "nan", "s/d", "sd"):
        return []
    return [int(x) for x in re.findall(r"\d+", s)]


def match_persona(nombre, E) -> tuple[int | None, str, float]:
    obj = norm(nombre)
    if not obj:
        return None, "", 0.0
    best = (None, "", 0.0)
    for pid, nom in zip(E["persona_id"], E["Nombre"]):
        sc = max(fuzz.token_sort_ratio(obj, norm(nom)), fuzz.ratio(obj, norm(nom)))
        if sc > best[2]:
            best = (pid, nom, round(sc, 1))
    return best


def nombre_similar(a, b) -> float:
    """0-100: qué tan parecidos son dos nombres (mismo criterio que match_persona,
    pero con token_set_ratio también, para tolerar que uno tenga palabras de más,
    p. ej. 'Mamerta Monteros' vs 'Mamerta Monteros -Escuela Sarmiento')."""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    return max(fuzz.token_sort_ratio(na, nb), fuzz.ratio(na, nb), fuzz.token_set_ratio(na, nb))


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    P = xl.parse("Premios")
    E = xl.parse("Expositoras")
    O = xl.parse("Objetos")
    K = xl.parse("Categorías")

    O15 = O[O["concurso_id"] == 1].merge(K, on="categoria_id")
    cat_id = K.set_index("nombre_categoria")["categoria_id"].to_dict()
    nombre_por_persona = E.set_index("persona_id")["Nombre"].to_dict()
    # quién es, hoy, el dueño real de cada objeto (para el chequeo final de nombre)
    nombre_por_objeto = O.assign(
        _nombre=O["expositora_id"].map(nombre_por_persona)
    ).set_index("objeto_id")["_nombre"].to_dict()

    manual: dict[int, dict] = {}
    if MANUAL.exists():
        for _, m in pd.read_csv(MANUAL, comment="#", dtype={"objeto_id": str}).dropna(how="all").iterrows():
            d = manual.setdefault(int(m["premio_id"]), {})
            obj_val = str(m.get("objeto_id", "")).strip().lower()
            if obj_val in ("ninguno", "sin_objeto", "sin objeto"):
                # fuerza a que quede SIN objeto (el cruce automático había
                # asignado uno equivocado): no correr el matching por número.
                d["sin_objeto"] = True
            elif pd.notna(m.get("objeto_id")) and obj_val not in ("", "nan"):
                d["objeto_id"] = int(m["objeto_id"])
            if pd.notna(m.get("persona_id")):
                d["persona_id"] = int(m["persona_id"])

    cols = {"persona_id": [], "persona": [], "persona_score": [],
            "objeto_id": [], "objeto_match": [], "candidato_rechazado": [], "revisar": []}

    for pid, r in P.iterrows():
        if pd.isna(r["NOMBRE"]):  # renglones de encabezado del fallo
            for c in cols:
                cols[c].append("")
            continue

        # --- persona ---
        per_id, per_nom, per_sc = match_persona(r["NOMBRE"], E)
        if pid in manual and "persona_id" in manual[pid]:
            per_id = manual[pid]["persona_id"]
            per_nom, per_sc = nombre_por_persona.get(per_id, ""), 100.0

        # --- objeto ---
        nums = parse_num(r["NÚM"])
        cat_label, obj_label = str(r["CATEGORÍA"]).strip(), str(r["OBJETO"]).strip()
        if cat_label in CROSSWALK:
            cats = CROSSWALK[cat_label]
        elif obj_label.lower() == "pañuelo":
            cats = ["PAÑUELOS"]
        else:
            cats = list(K["nombre_categoria"])  # ESTÍMULO / accésit -> todas
        cat_ids = {cat_id[c] for c in cats if c in cat_id}

        ids: list[int] = []
        metodo = ""
        if pid in manual and manual[pid].get("sin_objeto"):
            metodo = "sin objeto (forzado a mano: el cruce automático asignaba otra persona)"
        elif pid in manual and "objeto_id" in manual[pid]:
            ids, metodo = [manual[pid]["objeto_id"]], "manual"
        elif nums:
            base = O15[O15["categoria_id"].isin(cat_ids)]
            persona_confirmo = False  # el filtro de persona se aplicó de verdad en al menos un n
            for n in nums:
                sub = base[base["ORDEN"] == n]
                if per_id is not None and (sub["expositora_id"] == per_id).any():
                    sub = sub[sub["expositora_id"] == per_id]
                    persona_confirmo = True
                if len(sub) == 1:
                    ids.append(int(sub.iloc[0]["objeto_id"]))
                elif len(sub) > 1 and obj_label not in ("", "nan"):
                    sub = sub.assign(_s=sub["OBJETO"].map(
                        lambda t: fuzz.token_set_ratio(norm(obj_label), norm(t))))
                    ids.append(int(sub.sort_values("_s").iloc[-1]["objeto_id"]))
            # antes: "+persona" se agregaba solo por haber encontrado una persona con
            # ese nombre en algún lado del catálogo (per_id is not None), sin chequear
            # si esa persona tuvo algo que ver con el objeto elegido. Eso etiquetaba
            # como "confirmado por persona" casos donde el objeto era, en realidad, de
            # otra persona (único candidato para ese número, sin relación con el
            # nombre del premio). Ver docs/bitacora.md.
            metodo = "num+categoria" + ("+persona" if persona_confirmo else "")
        else:
            sub = O15[O15["categoria_id"].isin(cat_ids)]
            if per_id is not None:
                sub = sub[sub["expositora_id"] == per_id]
            if len(sub) == 1:
                ids, metodo = [int(sub.iloc[0]["objeto_id"])], "persona+categoria"
            elif len(sub) > 1 and obj_label not in ("", "nan"):
                sub = sub.assign(_s=sub["OBJETO"].map(
                    lambda t: fuzz.token_set_ratio(norm(obj_label), norm(t))))
                g = sub.sort_values("_s").iloc[-1]
                if g["_s"] >= 60:
                    ids, metodo = [int(g["objeto_id"])], f"persona+texto({int(g._s)})"

        # --- chequeo final: el nombre del premio, ¿se parece al del dueño real? ---
        # No se aplica a "manual" (decisión explícita a mano, se respeta tal cual).
        rechazado = ""
        if metodo != "manual" and ids:
            confirmados, rechazos = [], []
            for oid in ids:
                dueno = nombre_por_objeto.get(oid, "")
                score = nombre_similar(r["NOMBRE"], dueno)
                if score >= UMBRAL_NOMBRE:
                    confirmados.append(oid)
                else:
                    rechazos.append((oid, dueno, round(score, 1)))
            if rechazos:
                detalle = "; ".join(f"objeto {oid} es de {dueno!r} (score {sc})"
                                     for oid, dueno, sc in rechazos)
                rechazado = detalle
            ids = confirmados
            if not ids and rechazos:
                metodo = "rechazado por nombre: revisar a mano"

        fuera_cat = "fuera de cat" in str(r["OBSERVACIONES"]).lower()
        forzado_sin_objeto = pid in manual and manual[pid].get("sin_objeto")
        if not ids and not forzado_sin_objeto and not rechazado:
            metodo = "premio fuera de catálogo" if fuera_cat else "sin objeto: revisar a mano"
        revisar = "X" if (not ids or per_sc < 90) else ""

        cols["persona_id"].append(per_id if per_id is not None else "")
        cols["persona"].append(per_nom)
        cols["persona_score"].append(per_sc)
        cols["objeto_id"].append(";".join(map(str, ids)))
        cols["objeto_match"].append(metodo)
        cols["candidato_rechazado"].append(rechazado)
        cols["revisar"].append(revisar)

    salida = P.copy()
    for c, v in cols.items():
        salida[c] = v

    INTERIM.mkdir(parents=True, exist_ok=True)
    salida.to_excel(SALIDA, sheet_name="Premios", index=False)

    hechos = sum(1 for x in cols["objeto_id"] if x)
    rev = sum(1 for x in cols["revisar"] if x)
    print(f"{P['NOMBRE'].notna().sum()} premios | {hechos} con objeto_id | {rev} para revisar")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()
