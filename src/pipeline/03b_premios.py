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
                                   nombre, y de quién es en realidad; los candidatos
                                   cuando hay varios y nada permite elegir ("ambiguo:
                                   ..."); la persona descartada por parecido bajo
                                   UMBRAL_PERSONA_SOLA. Vacío si no pasó nada de eso
    revisar                        X sólo si queda algo por decidir: premio sin objeto
                                   y sin decisión, "pendiente" en premios_manual.csv,
                                   u objeto premiado dos veces. No se marcan los
                                   decididos a mano, los que el fallo da "fuera de
                                   catálogo" ni los vinculados con objeto confirmado

Correcciones a mano: data/interim/decisiones/premios_manual.csv
    premio_id,objeto_id,persona_id,nota
    (premio_id = número de fila 0-based de la hoja Premios; objeto_id="ninguno"
    fuerza a que quede sin objeto sin correr el cruce automático; objeto_id=
    "pendiente" no cambia el cruce pero deja la fila marcada con la nota como motivo)
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
# Premio sin objeto: la persona sale sólo del parecido de nombre contra todo el
# catálogo. Por debajo de esto se deja vacía en vez de adivinar (con 60-89 salían
# "Alejandrina Peiró" -> Valentina Pérez, "Rosa Barceló" -> Rosa Baralo).
UMBRAL_PERSONA_SOLA = 90
# Varios objetos con el mismo número: se elige por la dueña sólo si el nombre se
# parece de verdad. Con 60 "Marina Belmonte" se quedaba con el objeto de Isabel
# Maidana (62); los casos buenos dan 89-100.
UMBRAL_ELEGIR = 80

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
    # El fallo agrupa secciones que el catálogo separa: el punto de Irlanda de 1915
    # está en ENCAJES VARIOS (Argenia R. de Lautafy n.º 13, Corina Aguirre n.º 14) y
    # el fallo de bordados incluye deshilados (Sta Sandés n.º 24, "sección deshilados").
    # Con dos categorías un mismo número puede dar dos objetos: desempata la dueña.
    "BORDADO EN BLANCO Y SEDA": ["BORDADO EN BLANCO Y SEDA", "DESHILADO"],
    "CROCHET E IRLANDA": ["CROCHET", "ENCAJES VARIOS"],
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


def variantes(nombre) -> list[str]:
    """Las lecturas posibles de un nombre con corchetes, ya normalizadas.

    Los corchetes marcan la variante con que otra fuente nombra a la misma persona
    (ver docs/bitacora.md): 'Delicia [Delia] Ruiz' es 'Delicia Ruiz' o 'Delia Ruiz';
    'Rosa V. [de] Lescano' es 'Rosa V. Lescano' o 'Rosa V. de Lescano'. Comparar el
    texto con los corchetes adentro hacía que el fallo no matcheara con su dueña.
    """
    s = str(nombre)
    m = re.search(r"\[(.*?)\]", s)
    if not m:
        return [norm(s)]
    antes, dentro, despues = s[:m.start()], m.group(1), s[m.end():]
    palabras = antes.split()
    reemplazo = " ".join(palabras[:-1] + [dentro]) if palabras else dentro
    lecturas = {antes + despues,                 # sin la variante
                antes + dentro + despues,        # la variante como palabra agregada
                reemplazo + despues}             # la variante en lugar de la palabra anterior
    return [v for v in {norm(x) for x in lecturas} if v]


def _score(a, b, *scorers) -> float:
    na = norm(a)
    if not na:
        return 0.0
    return max((sc(na, v) for v in variantes(b) for sc in scorers), default=0.0)


def match_persona(nombre, E) -> tuple[int | None, str, float]:
    if not norm(nombre):
        return None, "", 0.0
    best = (None, "", 0.0)
    for pid, nom in zip(E["persona_id"], E["Nombre"]):
        sc = _score(nombre, nom, fuzz.token_sort_ratio, fuzz.ratio)
        if sc > best[2]:
            best = (pid, nom, round(sc, 1))
    return best


def nombre_similar(a, b) -> float:
    """0-100: qué tan parecidos son dos nombres (mismo criterio que match_persona,
    pero con token_set_ratio también, para tolerar que uno tenga palabras de más,
    p. ej. 'Mamerta Monteros' vs 'Mamerta Monteros -Escuela Sarmiento')."""
    return _score(a, b, fuzz.token_sort_ratio, fuzz.ratio, fuzz.token_set_ratio)


def elegir(sub: pd.DataFrame, nombre_premio, obj_label: str,
           nombre_por_objeto: dict) -> tuple[int | None, str]:
    """Entre varios objetos candidatos, elige uno. Devuelve (objeto_id, nota).

    1. el de la dueña cuyo nombre más se parece al del premio, si supera
       UMBRAL_ELEGIR y no empata con otro;
    2. si no, el de texto más parecido al OBJETO del fallo (criterio anterior);
    3. si tampoco hay texto, ninguno: la nota lista los candidatos para decidir a mano.
    """
    sc = sub["objeto_id"].map(lambda o: nombre_similar(nombre_premio, nombre_por_objeto.get(o, "")))
    top = sc.max()
    if top >= UMBRAL_ELEGIR and (sc == top).sum() == 1:
        return int(sub.loc[sc.idxmax(), "objeto_id"]), ""
    if obj_label not in ("", "nan"):
        s = sub.assign(_s=sub["OBJETO"].map(lambda t: fuzz.token_set_ratio(norm(obj_label), norm(t))))
        return int(s.sort_values("_s").iloc[-1]["objeto_id"]), ""
    nota = "ambiguo: " + " / ".join(
        f"{int(o)} {c} ({nombre_por_objeto.get(o, '')})"
        for o, c in zip(sub["objeto_id"], sub["nombre_categoria"]))
    return None, nota


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
    dueno_por_objeto = O.set_index("objeto_id")["expositora_id"].to_dict()

    manual: dict[int, dict] = {}
    if MANUAL.exists():
        for _, m in pd.read_csv(MANUAL, comment="#", dtype={"objeto_id": str}).dropna(how="all").iterrows():
            d = manual.setdefault(int(m["premio_id"]), {})
            obj_val = str(m.get("objeto_id", "")).strip().lower()
            if pd.notna(m.get("nota")):
                d["nota"] = str(m["nota"]).strip()
            if obj_val in ("ninguno", "sin_objeto", "sin objeto"):
                # fuerza a que quede SIN objeto (el cruce automático había
                # asignado uno equivocado, o es un premio fuera de catálogo):
                # no correr el matching por número.
                d["sin_objeto"] = True
            elif obj_val == "pendiente":
                # duda abierta: el cruce sigue igual, pero la fila queda marcada
                d["pendiente"] = True
            elif pd.notna(m.get("objeto_id")) and obj_val not in ("", "nan"):
                d["objeto_id"] = int(m["objeto_id"])
            if pd.notna(m.get("persona_id")):
                d["persona_id"] = int(m["persona_id"])

    # Vínculos resueltos a mano dentro de la propia hoja Premios (objeto_match =
    # "Revisado a mano"), anteriores a premios_manual.csv. Sin esto se perdían: el
    # premio de Dominga Nieva cita el n.º 9 y su colcha es el n.º 4 del catálogo
    # (objeto 104). Lo que diga premios_manual.csv tiene prioridad.
    if "objeto_match" in P.columns:
        for pid, r in P.iterrows():
            if str(r["objeto_match"]).strip().lower() != "revisado a mano":
                continue
            d = manual.setdefault(pid, {})
            if pd.notna(r.get("objeto_id")) and not d.get("sin_objeto"):
                d.setdefault("objeto_id", int(float(str(r["objeto_id"]).split(";")[0])))
            if pd.notna(r.get("persona_id")):
                d.setdefault("persona_id", int(r["persona_id"]))

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
        ambiguos: list[str] = []
        if pid in manual and manual[pid].get("sin_objeto"):
            nota = manual[pid].get("nota", "")
            metodo = f"decisión a mano: {nota}" if nota else \
                "sin objeto (forzado a mano: el cruce automático asignaba otra persona)"
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
                elif len(sub) > 1:
                    oid, nota = elegir(sub, r["NOMBRE"], obj_label, nombre_por_objeto)
                    if oid is not None:
                        ids.append(oid)
                    else:
                        ambiguos.append(f"n.º {n} {nota}")
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
            elif len(sub) > 1:
                ambiguos.append("ambiguo: " + " / ".join(
                    f"{int(o)} {c}" for o, c in zip(sub["objeto_id"], sub["nombre_categoria"])))

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

        # --- persona = dueña del objeto confirmado ---
        # La persona se eligió arriba sólo por parecido de nombre, contra todo el
        # catálogo; si el objeto quedó confirmado (número + categoría + nombre), su
        # dueña es mejor evidencia. Sin esto, "Mercedes Pereyra" quedaba con
        # Mercedes Pérez aunque el objeto 174 fuera de María Mercedes Pereira.
        duenas = {dueno_por_objeto.get(oid) for oid in ids}
        manual_persona = pid in manual and "persona_id" in manual[pid]
        if len(duenas) == 1 and None not in duenas and not manual_persona:
            duena = duenas.pop()
            if duena != per_id:
                per_id = duena
                per_nom = nombre_por_persona.get(duena, "")
                per_sc = round(nombre_similar(r["NOMBRE"], per_nom), 1)

        fuera_cat = "fuera de cat" in str(r["OBSERVACIONES"]).lower()
        forzado_sin_objeto = pid in manual and manual[pid].get("sin_objeto")
        if not ids and not forzado_sin_objeto and not rechazado:
            metodo = "premio fuera de catálogo" if fuera_cat else "sin objeto: revisar a mano"
            if ambiguos:
                metodo = "varios candidatos: revisar a mano"
                rechazado = "; ".join(ambiguos)

        # Sin objeto que la respalde, la persona es sólo un parecido de nombre.
        if not ids and not manual_persona and per_id is not None and per_sc < UMBRAL_PERSONA_SOLA:
            rechazado = "; ".join(x for x in (rechazado,
                f"persona descartada: {per_nom!r} (score {per_sc})") if x)
            per_id, per_nom, per_sc = None, "", 0.0
        # Antes se marcaba todo premio sin objeto o con parecido de nombre < 90: salían
        # 23, de los cuales sólo 5 estaban abiertos. Ahora sólo lo que falta decidir.
        decidido = pid in manual and ("objeto_id" in manual[pid] or manual[pid].get("sin_objeto"))
        pendiente = pid in manual and manual[pid].get("pendiente")
        if pendiente:
            metodo = f"{metodo} · PENDIENTE: {manual[pid].get('nota', '')}"
        revisar = "X" if pendiente or (not ids and not decidido and not fuera_cat) else ""

        cols["persona_id"].append(per_id if per_id is not None else "")
        cols["persona"].append(per_nom)
        cols["persona_score"].append(per_sc)
        cols["objeto_id"].append(";".join(map(str, ids)))
        cols["objeto_match"].append(metodo)
        cols["candidato_rechazado"].append(rechazado)
        cols["revisar"].append(revisar)

    # Un objeto premiado dos veces casi siempre es un vínculo de más (p. ej. un
    # premio "s/d" que cae por persona+categoría sobre un objeto que ya tiene su
    # premio). No se decide cuál sobra: se marcan los dos para revisar.
    usos: dict[int, list[int]] = {}
    for i, ids_txt in enumerate(cols["objeto_id"]):
        for oid in filter(None, str(ids_txt).split(";")):
            usos.setdefault(int(oid), []).append(i)
    for oid, filas in usos.items():
        if len(filas) < 2:
            continue
        for i in filas:
            otras = ", ".join(str(j) for j in filas if j != i)
            cols["candidato_rechazado"][i] = "; ".join(x for x in (
                cols["candidato_rechazado"][i],
                f"objeto {oid} también premiado en premio_id {otras}") if x)
            cols["revisar"][i] = "X"

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
