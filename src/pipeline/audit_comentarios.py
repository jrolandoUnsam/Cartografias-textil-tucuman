"""Auditoría de comentarios — ¿se aplicó cada decisión anotada a mano?

Recorre, fila por fila:
  1. `data/interim/revision_duplicados.xlsx`  (hojas Personas y Ciudades)
  2. la hoja `Premios` original (tabla manual, vía `tabla_normalizada_dedup.xlsx`),
     columnas de comentario "Mis comentarios" / "Coment LM", contra el vínculo
     vigente de la hoja `Premios` curada (`04e_premios`)

y compara la decisión que dice el comentario contra el estado actual de
`tabla_normalizada.xlsx`, tomando como línea de base `tabla_normalizada_manual.xlsx`
(la tabla antes del pipeline).

Escribe un informe reproducible en `docs/auditoria_comentarios.md`.

Veredictos:
  SIN HACER      la fila sigue igual que en la línea de base; no se aplicó nada
  SOLO NOMBRE    se normalizó/corrigió el nombre, pero las filas NO se fusionaron
  FUSIÓN OK      una fila desapareció y quedó la que pide el comentario
  FUSIÓN REVISAR una fila desapareció pero quedó la otra / el nombre no coincide
  OK SEPARAR     se pidió NO unificar y siguen las dos filas
  CONTRA LO PEDIDO  se pidió separar y se fusionó (o al revés)
  OBJETOS PARTIDOS  además: hay objetos en la fila que el comentario descarta
  FUSIÓN OK (en un tercer id)  las dos desaparecieron porque entraron en un grupo
                 de 3+ y quedó otro id con los objetos de ambas
  DUDA ABIERTA   el comentario sólo pregunta ("J o I?"): no hay decisión que verificar
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

from _util import INTERIM, PROCESSED, RAIZ, limpiar_texto

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
REVISION = INTERIM / "revision_duplicados.xlsx"
INFORME = RAIZ / "docs" / "auditoria_comentarios.md"

# Línea de base: la tabla tal como la dejó la investigadora, ANTES de que el
# pipeline aplicara ninguna decisión.
BASE = INTERIM / "tabla_normalizada_manual.xlsx"
FUSIONES = INTERIM / "decisiones" / "fusiones_expositoras.csv"

SEP_KW = [
    "no lo unificar", "no la unir", "no las unir", "dejaría así", "separad",
    "mantendría como está", "de momento no", "madre e hija",
    "no son la misma", "no son el mismo", "estas no son", "no queda claro",
]


# "dejaría cada ciudad como está" (Dalmira González Sorol) habla de la ciudad de cada
# envío, no de separar a la persona: la ciudad va en cada objeto y sobrevive a la
# fusión. Antes "dejaría cada" estaba en SEP_KW y daba un falso "CONTRA LO PEDIDO".
CIUDAD_KW = ["cada ciudad"]

# Un comentario que sólo pregunta ("J o I? ...") no es una decisión de unificar.
DECIDE_KW = ["unifi", "dejamos", "dejar", "vamos con", "mantenerlo", "con tilde"]


def tildes(s: str) -> bool:
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", str(s)))


def tiene_de(s: str) -> bool:
    return bool(re.search(r"\b(de|del)\b", str(s).lower()))


def lado_a_conservar(com: str, na: str, nb: str) -> str | None:
    """Devuelve 'A', 'B' o None según el texto del comentario."""
    c = com.lower()
    if "dejamos b" in c or "dejamos el b" in c or "vamos con b" in c or "dejar b" in c:
        return "B"
    if "dejamos a" in c or "dejamos el a" in c or "dejar a" in c or "info a" in c:
        return "A"
    if "con tilde" in c:
        if tildes(na) and not tildes(nb):
            return "A"
        if tildes(nb) and not tildes(na):
            return "B"
        return None
    if "mantenerlo" in c or c.startswith("de /") or "dejamos del" in c:
        if tiene_de(na) and not tiene_de(nb):
            return "A"
        if tiene_de(nb) and not tiene_de(na):
            return "B"
    return None


def destino_fusion(pid: int, Og: pd.DataFrame, O: pd.DataFrame) -> set[int]:
    """Ids que tienen hoy los objetos que `pid` tenía en la línea de base. Si no
    tenía objetos, el id que lo absorbe según decisiones/fusiones_expositoras.csv."""
    objs = Og.loc[Og["expositora_id"] == pid, "objeto_id"]
    destinos = set(O.loc[O["objeto_id"].isin(objs), "expositora_id"])
    if not destinos and FUSIONES.exists():
        F = pd.read_csv(FUSIONES, dtype=str)
        for mantener, descartar in zip(F["mantener"], F["descartar"]):
            if str(pid) in str(descartar).split():
                destinos.add(int(mantener))
    return destinos


def audita_personas(md: list[str]) -> None:
    xl = pd.ExcelFile(FUENTE)
    E, O = xl.parse("Expositoras"), xl.parse("Objetos")
    g = pd.ExcelFile(BASE)
    Eg, Og = g.parse("Expositoras"), g.parse("Objetos")
    ids = set(E["persona_id"])
    nom = E.set_index("persona_id")["Nombre"].to_dict()
    nom_g = Eg.set_index("persona_id")["Nombre"].to_dict()
    n_obj = O.groupby("expositora_id").size().to_dict()

    rev = pd.read_excel(REVISION, sheet_name="Personas - candidatos")

    filas: list[str] = []
    tally: dict[str, int] = {}
    md.append("## 1. `revision_duplicados.xlsx` — hoja *Personas - candidatos*\n")
    cab = (
        "| # | id A / nombre | id B / nombre | Hecho | Comentario | Decisión leída | "
        "Estado actual | Veredicto |\n"
        "|---|---|---|---|---|---|---|---|"
    )

    for i, r in rev.iterrows():
        a, b = int(r["id_A"]), int(r["id_B"])
        com = "" if pd.isna(r["Comentarios"]) else str(r["Comentarios"]).replace("\n", " ").strip()
        hecho = str(r["Hecho"])
        na_now, nb_now = nom.get(a, "—"), nom.get(b, "—")
        ea, eb = a in ids, b in ids
        oa, ob = n_obj.get(a, 0), n_obj.get(b, 0)
        cl = com.lower()

        separar = any(k in cl for k in SEP_KW)
        duda = "?" in cl and not separar and not any(k in cl for k in DECIDE_KW)
        lado = lado_a_conservar(com, str(r["nombre_A"]), str(r["nombre_B"]))
        if separar:
            decision = "Mantener SEPARADAS"
        elif duda:
            decision = "Duda (sin decisión)"
        elif any(k in cl for k in CIUDAD_KW):
            decision = "Unificar (la ciudad queda en cada objeto)"
        elif lado == "A":
            decision = f"Unificar → conservar A ({a})"
        elif lado == "B":
            decision = f"Unificar → conservar B ({b})"
        elif com:
            decision = "Unificar (cualquiera de las dos)"
        else:
            decision = "(sin comentario)"

        # estado actual
        cambio_nombre = str(na_now) != str(nom_g.get(a)) or str(nb_now) != str(nom_g.get(b))
        if ea and eb:
            estado = f"2 filas · A:{oa} obj, B:{ob} obj"
        elif ea or eb:
            vive = a if ea else b
            estado = f"1 fila: {vive} ({nom.get(vive)}) · {n_obj.get(vive, 0)} obj"
        else:
            # Las dos desaparecieron: casi siempre porque entraron en un grupo de 3+
            # y quedó un tercer id (p. ej. 313 y 319 -> 196 Concepción de Pérez).
            destinos = destino_fusion(a, Og, O) | destino_fusion(b, Og, O)
            if len(destinos) == 1:
                d = destinos.pop()
                estado = f"las dos fusionadas en `{d}` ({nom.get(d)}) · {n_obj.get(d, 0)} obj"
            else:
                estado = "ninguna de las dos existe"

        # veredicto
        if separar:
            v = "OK SEPARAR" if (ea and eb) else "⚠ CONTRA LO PEDIDO (se fusionó)"
        elif duda:
            v = "DUDA ABIERTA" if (ea and eb) else "fusionada (el comentario era una duda)"
        elif ea and eb:
            v = "SOLO NOMBRE" if cambio_nombre else "SIN HACER"
            descartada = a if lado == "B" else (b if lado == "A" else None)
            if descartada is not None and n_obj.get(descartada, 0) > 0:
                v += " · OBJETOS PARTIDOS"
        elif ea ^ eb:
            vive = a if ea else b
            quien = "A" if ea else "B"
            if lado is None or lado == quien:
                v = "FUSIÓN OK"
            else:
                v = f"⚠ FUSIÓN REVISAR (se pidió {lado}, quedó {quien})"
        elif estado.startswith("las dos fusionadas"):
            v = "FUSIÓN OK (en un tercer id)"
        else:
            v = "⚠ ninguna existe"

        clave = v.split(" · ")[0].replace("⚠ ", "")
        tally[clave] = tally.get(clave, 0) + 1
        filas.append(
            f"| {i + 1} | `{a}` {na_now} | `{b}` {nb_now} | {hecho} | {com or '—'} | "
            f"{decision} | {estado} | **{v}** |"
        )

    md.append("_Conteo:_ " + " · ".join(f"{k}: {n}" for k, n in sorted(tally.items())) + "\n")
    md.append(cab)
    md.extend(filas)


def audita_ciudades(md: list[str]) -> None:
    xl = pd.ExcelFile(FUENTE)
    C, O = xl.parse("Ciudades"), xl.parse("Objetos")
    ids = set(C["ciudad_id"])
    # ciudad conocida sólo por la provincia (p. ej. 9, Córdoba): se muestra la provincia
    nom = C.set_index("ciudad_id")["nombre_ciudad"].fillna(
        C.set_index("ciudad_id")["nombre_provincia"]).to_dict()
    n_obj = O.groupby("ciudad_id").size().to_dict()
    rev = pd.read_excel(REVISION, sheet_name="Ciudades - candidatos")
    col_com = "Comentarios" if "Comentarios" in rev.columns else "Comendatios"

    md.append("\n## 2. `revision_duplicados.xlsx` — hoja *Ciudades - candidatos*\n")
    md.append(
        "| # | id A / nombre | id B / nombre | Hecho | Comentario | "
        "Estado actual | Veredicto |\n"
        "|---|---|---|---|---|---|---|"
    )
    for i, r in rev.iterrows():
        a, b = int(r["id_A"]), int(r["id_B"])
        com = "" if pd.isna(r[col_com]) else str(r[col_com]).strip()
        ea, eb = a in ids, b in ids
        if ea and eb:
            estado = f"2 filas · A:{n_obj.get(a, 0)} obj, B:{n_obj.get(b, 0)} obj"
        elif ea ^ eb:
            vive = a if ea else b
            estado = f"1 fila: {vive} ({nom.get(vive)})"
        else:
            estado = "ninguna existe"
        hecho = str(r["Hecho"])
        if hecho.lower() == "true" and (ea ^ eb):
            v = "FUSIÓN OK"
        elif hecho.lower() == "true" and ea and eb:
            v = "SIN HACER (marcado Hecho)"
        elif ea and eb:
            v = "OK SEPARAR"
        else:
            v = "revisar"
        md.append(
            f"| {i + 1} | `{a}` {r['nombre_A']} | `{b}` {r['nombre_B']} | {hecho} | "
            f"{com or '—'} | {estado} | **{v}** |"
        )


def audita_premios(md: list[str]) -> None:
    xl = pd.ExcelFile(FUENTE)
    # Los comentarios viven en la hoja Premios original (tabla manual, vía 04); el
    # vínculo vigente, en la hoja curada que arma 04e. Se cruzan por premio_id (fila).
    P = pd.read_excel(INTERIM / "tabla_normalizada_dedup.xlsx", sheet_name="Premios")
    vigente = xl.parse("Premios").set_index("premio_id")["objeto_id"]
    P["objeto_id"] = P.index.map(vigente)
    E = xl.parse("Expositoras")
    O = xl.parse("Objetos")
    g = pd.ExcelFile(BASE)
    Pg = g.parse("Premios")
    nom_exp = E.set_index("persona_id")["Nombre"].to_dict()
    exp_de_obj = O.set_index("objeto_id")["expositora_id"].to_dict()
    cols_com = [c for c in P.columns if "coment" in c.lower()]

    cols_orig = list(Pg.columns[:8])  # PREMIOS … NÚM: lo que transcribe el fallo
    # 04 limpia espacios de más en todas las celdas: eso no cuenta como modificación
    txt = lambda s: s.map(limpiar_texto).fillna("").astype(str)
    intactas = all((txt(P[c]) == txt(Pg[c])).all() for c in cols_orig)

    md.append("\n## 3. `tabla_normalizada.xlsx` — hoja *Premios* (filas con comentario)\n")
    md.append(
        f"> Las 8 columnas originales de la hoja Premios están **{'intactas' if intactas else 'MODIFICADAS'}** "
        "respecto de la tabla de partida (sin contar espacios de más). El vínculo que se muestra "
        "es el de la hoja curada de `04e_premios.py`.\n"
        ">\n"
        "> Los comentarios de esta hoja son **observaciones sobre nombres**, no órdenes de "
        "fusión. La columna *Nombre real de la expositora* muestra a quién apunta hoy el "
        "`objeto_id` de esa fila (vía `Objetos.expositora_id`).\n"
    )
    md.append(
        "| premio_id | NOMBRE en el fallo | objeto_id | Nombre real de la expositora (hoy) | "
        "Comentario(s) | Estado |\n"
        "|---|---|---|---|---|---|"
    )
    for i, r in P.iterrows():
        coms = [f"**{c}:** {str(r[c]).strip()}" for c in cols_com if pd.notna(r[c])]
        if not coms:
            continue
        obj_raw = r.get("objeto_id")
        obj = "" if pd.isna(obj_raw) else str(obj_raw)
        reales = []
        for tok in re.findall(r"\d+", obj):
            pid = exp_de_obj.get(int(tok))
            if pid is not None:
                reales.append(nom_exp.get(pid, f"id {pid}"))
        real = " ; ".join(dict.fromkeys(reales)) if reales else "— (el premio no tiene objeto en el catálogo)"

        c = " ".join(coms).lower()
        if not obj:
            estado = "decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún)"
        elif "ezequiela" in c and "esequiela" in c:
            estado = ("resuelto: la expositora ya figura como 'Ezequiela'"
                      if "ezequiela" in real.lower() else
                      "PENDIENTE: LM pide 'Ezequiela'; la expositora sigue como 'Esequiela'")
        elif "Coment LM" in cols_com and pd.notna(r["Coment LM"]):
            estado = "respondida por LM — el nombre que quedó está en 'Nombre real'"
        else:
            estado = "observación sin respuesta de LM"
        md.append(
            f"| {i} | {r['NOMBRE']} | {obj or '—'} | {real} | {' / '.join(coms)} | {estado} |"
        )


def hallazgo_global() -> str:
    """Compara la tabla actual contra la línea de base y describe el estado real.

    Esta frase se calcula, no se escribe a mano: el encabezado de este informe
    llegó a afirmar lo contrario de lo que decían sus propias filas.
    """
    a = pd.ExcelFile(FUENTE)
    b = pd.ExcelFile(BASE)
    Ea, Eg = a.parse("Expositoras"), b.parse("Expositoras")
    Oa, Og = a.parse("Objetos"), b.parse("Objetos")

    reasignados = 0
    if len(Oa) == len(Og):
        por_id = Og.set_index("objeto_id")["expositora_id"].to_dict()
        reasignados = sum(
            1 for oid, eid in zip(Oa["objeto_id"], Oa["expositora_id"])
            if oid in por_id and por_id[oid] != eid
        )
    borradas = len(set(Eg["persona_id"]) - set(Ea["persona_id"]))

    nom_a = Ea.set_index("persona_id")["Nombre"].to_dict()
    nom_g = Eg.set_index("persona_id")["Nombre"].to_dict()
    renombradas = sum(1 for k, v in nom_a.items()
                      if k in nom_g and str(nom_g[k]) != str(v))

    if reasignados == 0 and borradas == 0:
        estado = ("la hoja `Objetos` es **idéntica** a la tabla de partida "
                  "(`tabla_normalizada_manual.xlsx`): ningún `expositora_id` se "
                  "reasignó, así que "
                  "**ninguna fusión de expositoras se aplicó a la tabla**")
    else:
        estado = (f"respecto de la tabla de partida "
                  f"(`tabla_normalizada_manual.xlsx`) se reasignaron "
                  f"**{reasignados} objetos** y desaparecieron **{borradas} filas** "
                  f"de `Expositoras`: las fusiones **sí** están aplicadas")
    return f"**Hallazgo global:** {estado}. Nombres normalizados: {renombradas}.\n"


def main() -> None:
    md: list[str] = [
        "# Auditoría de comentarios — estado de aplicación\n",
        f"_Generado por `src/pipeline/audit_comentarios.py` — no editar a mano._\n",
        "Compara cada decisión anotada a mano contra el estado actual de "
        "`data/processed/tabla_normalizada.xlsx`, tomando como línea de base "
        "`data/interim/tabla_normalizada_manual.xlsx` (la tabla antes del pipeline).\n",
        hallazgo_global(),
        "**Veredictos:**\n"
        "- `SIN HACER` — la fila sigue igual que en la línea de base.\n"
        "- `SOLO NOMBRE` — se corrigió/normalizó el nombre, pero las dos filas **siguen "
        "sin fusionar** (los objetos no se movieron).\n"
        "- `SOLO NOMBRE · OBJETOS PARTIDOS` — ídem, y además hay objetos en la fila que "
        "el comentario manda descartar → fusionar no es solo borrar.\n"
        "- `FUSIÓN OK` — una fila desapareció y quedó la que pide el comentario.\n"
        "- `FUSIÓN REVISAR` — una fila desapareció pero quedó la otra.\n"
        "- `OK SEPARAR` — se pidió **no** unificar y siguen las dos filas (correcto).\n"
        "- `CONTRA LO PEDIDO` — se pidió separar y se fusionó, o al revés.\n"
        "- `FUSIÓN OK (en un tercer id)` — las dos filas desaparecieron porque entraron "
        "en un grupo de 3 o más; sus objetos están juntos en otro id.\n"
        "- `DUDA ABIERTA` — el comentario sólo pregunta; no hay decisión que verificar.\n",
    ]
    audita_personas(md)
    audita_ciudades(md)
    audita_premios(md)
    INFORME.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"-> {INFORME}")


if __name__ == "__main__":
    main()
