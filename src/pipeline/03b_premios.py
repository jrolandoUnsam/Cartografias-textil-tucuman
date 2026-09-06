"""Etapa 03b — Vincular cada línea de la hoja `Premios` con la hoja `Objetos`.

Toma la hoja `Premios` de `tabla_normalizada.xlsx` (fallo del jurado de 1915) y le
agrega, fila por fila y en el mismo orden, dos columnas:

    persona_id   ->  Expositoras.persona_id  (por nombre)
    objeto_id    ->  Objetos.objeto_id       (por categoría + N.º de orden + persona)

Salida: data/interim/premios_vinculados.xlsx  (hoja única, misma cantidad de filas
que `Premios`, lista para copiar las columnas nuevas a tu Excel).

Columnas agregadas:
    persona_id, persona            expositora resuelta y su nombre normalizado
    persona_score                  0-100; < 90 = revisar
    objeto_id                      id del objeto; varios ids separados por ";" si el
                                   premio abarca un rango ("17, 18, 19, 20 y 21")
    objeto_match                   cómo se resolvió, o el motivo si quedó vacío
    revisar                        X si hay que mirarlo a mano

Correcciones a mano: data/interim/decisiones/premios_manual.csv
    premio_id,objeto_id,persona_id,nota
    (premio_id = número de fila 0-based de la hoja Premios)
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


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    P = xl.parse("Premios")
    E = xl.parse("Expositoras")
    O = xl.parse("Objetos")
    K = xl.parse("Categorías")

    O15 = O[O["concurso_id"] == 1].merge(K, on="categoria_id")
    cat_id = K.set_index("nombre_categoria")["categoria_id"].to_dict()
    nombre_por_persona = E.set_index("persona_id")["Nombre"].to_dict()

    manual: dict[int, dict] = {}
    if MANUAL.exists():
        for _, m in pd.read_csv(MANUAL, comment="#").dropna(how="all").iterrows():
            d = manual.setdefault(int(m["premio_id"]), {})
            if pd.notna(m.get("objeto_id")):
                d["objeto_id"] = int(m["objeto_id"])
            if pd.notna(m.get("persona_id")):
                d["persona_id"] = int(m["persona_id"])

    cols = {"persona_id": [], "persona": [], "persona_score": [],
            "objeto_id": [], "objeto_match": [], "revisar": []}

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
        if pid in manual and "objeto_id" in manual[pid]:
            ids, metodo = [manual[pid]["objeto_id"]], "manual"
        elif nums:
            base = O15[O15["categoria_id"].isin(cat_ids)]
            for n in nums:
                sub = base[base["ORDEN"] == n]
                if per_id is not None and (sub["expositora_id"] == per_id).any():
                    sub = sub[sub["expositora_id"] == per_id]
                if len(sub) == 1:
                    ids.append(int(sub.iloc[0]["objeto_id"]))
                elif len(sub) > 1 and obj_label not in ("", "nan"):
                    sub = sub.assign(_s=sub["OBJETO"].map(
                        lambda t: fuzz.token_set_ratio(norm(obj_label), norm(t))))
                    ids.append(int(sub.sort_values("_s").iloc[-1]["objeto_id"]))
            metodo = "num+categoria" + ("+persona" if per_id is not None else "")
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

        fuera_cat = "fuera de cat" in str(r["OBSERVACIONES"]).lower()
        if not ids:
            metodo = "premio fuera de catálogo" if fuera_cat else "sin objeto: revisar a mano"
        revisar = "X" if (not ids or per_sc < 90) else ""

        cols["persona_id"].append(per_id if per_id is not None else "")
        cols["persona"].append(per_nom)
        cols["persona_score"].append(per_sc)
        cols["objeto_id"].append(";".join(map(str, ids)))
        cols["objeto_match"].append(metodo)
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
