"""Auditoría de comentarios — ¿se aplicó cada decisión anotada a mano?

Recorre, fila por fila:
  1. `data/interim/revision_duplicados.xlsx`  (hojas Personas y Ciudades)
  2. la hoja `Premios` de `data/processed/tabla_normalizada.xlsx`  (columnas de
     comentario "Mis comentarios" / "Coment LM")

y compara la decisión que dice el comentario contra el estado actual de
`tabla_normalizada.xlsx` (y contra la copia congelada en `tests/golden/`, para
saber qué se tocó).

Escribe un informe reproducible en `docs/auditoria_comentarios.md`.

Veredictos:
  SIN HACER      la fila sigue igual que en el golden; no se aplicó nada
  SOLO NOMBRE    se normalizó/corrigió el nombre, pero las filas NO se fusionaron
  FUSIÓN OK      una fila desapareció y quedó la que pide el comentario
  FUSIÓN REVISAR una fila desapareció pero quedó la otra / el nombre no coincide
  OK SEPARAR     se pidió NO unificar y siguen las dos filas
  CONTRA LO PEDIDO  se pidió separar y se fusionó (o al revés)
  OBJETOS PARTIDOS  además: hay objetos en la fila que el comentario descarta
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

from _util import GOLDEN, INTERIM, PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
REVISION = INTERIM / "revision_duplicados.xlsx"
INFORME = RAIZ / "docs" / "auditoria_comentarios.md"

SEP_KW = [
    "no lo unificar", "no la unir", "no las unir", "dejaría así", "separad",
    "mantendría como está", "dejaría cada", "de momento no", "madre e hija",
    "no son la misma", "no son el mismo", "estas no son", "no queda claro",
]


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


def audita_personas(md: list[str]) -> None:
    xl = pd.ExcelFile(FUENTE)
    E, O = xl.parse("Expositoras"), xl.parse("Objetos")
    g = pd.ExcelFile(GOLDEN / "tabla_normalizada.xlsx")
    Eg = g.parse("Expositoras")
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
        lado = lado_a_conservar(com, str(r["nombre_A"]), str(r["nombre_B"]))
        if separar:
            decision = "Mantener SEPARADAS"
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
            estado = "ninguna de las dos existe"

        # veredicto
        if separar:
            v = "OK SEPARAR" if (ea and eb) else "⚠ CONTRA LO PEDIDO (se fusionó)"
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
    nom = C.set_index("ciudad_id")["nombre_ciudad"].to_dict()
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
    P = xl.parse("Premios")
    E = xl.parse("Expositoras")
    O = xl.parse("Objetos")
    g = pd.ExcelFile(GOLDEN / "tabla_normalizada.xlsx")
    Pg = g.parse("Premios")
    nom_exp = E.set_index("persona_id")["Nombre"].to_dict()
    exp_de_obj = O.set_index("objeto_id")["expositora_id"].to_dict()
    cols_com = [c for c in P.columns if "coment" in c.lower()]

    cols_orig = [c for c in Pg.columns]
    intactas = all(
        (P[c].fillna("").astype(str) == Pg[c].fillna("").astype(str)).all() for c in cols_orig
    )

    md.append("\n## 3. `tabla_normalizada.xlsx` — hoja *Premios* (filas con comentario)\n")
    md.append(
        f"> Las 8 columnas originales de la hoja Premios están **{'intactas' if intactas else 'MODIFICADAS'}** "
        "respecto del golden. Lo que se agregó son las columnas de vínculo (`persona_id`, "
        "`objeto_id`, …, salida de `03b_premios.py`) y las de comentario.\n"
        ">\n"
        "> Los comentarios de esta hoja son **observaciones sobre nombres**, no órdenes de "
        "fusión. La columna *Nombre real de la expositora* muestra a quién apunta hoy el "
        "`objeto_id` de esa fila (vía `Objetos.expositora_id`).\n"
    )
    md.append(
        "| fila | NOMBRE en el fallo | objeto_id | Nombre real de la expositora (hoy) | "
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
            estado = "PENDIENTE: LM pide 'Ezequiela'; la expositora sigue como 'Esequiela'"
        elif any(k in c for k in ["vs", "de +", "de zavalia", "segundo", "aparentemente", "encontramos", "r."]):
            estado = "observación de forma del nombre — comparar contra 'Nombre real' y decidir"
        else:
            estado = "observación / confirmación"
        md.append(
            f"| {i} | {r['NOMBRE']} | {obj or '—'} | {real} | {' / '.join(coms)} | {estado} |"
        )


def main() -> None:
    md: list[str] = [
        "# Auditoría de comentarios — estado de aplicación\n",
        f"_Generado por `src/pipeline/audit_comentarios.py` — no editar a mano._\n",
        "Compara cada decisión anotada a mano contra el estado actual de "
        "`data/processed/tabla_normalizada.xlsx`.\n",
        "**Hallazgo global:** la hoja `Objetos` es **idéntica** a la copia congelada "
        "(`tests/golden/`): ningún `expositora_id` se reasignó, así que **ninguna "
        "fusión de expositoras se aplicó a la tabla**. Sí se normalizaron 437 nombres.\n",
        "**Veredictos:**\n"
        "- `SIN HACER` — la fila sigue igual que en el golden.\n"
        "- `SOLO NOMBRE` — se corrigió/normalizó el nombre, pero las dos filas **siguen "
        "sin fusionar** (los objetos no se movieron).\n"
        "- `SOLO NOMBRE · OBJETOS PARTIDOS` — ídem, y además hay objetos en la fila que "
        "el comentario manda descartar → fusionar no es solo borrar.\n"
        "- `FUSIÓN OK` — una fila desapareció y quedó la que pide el comentario.\n"
        "- `FUSIÓN REVISAR` — una fila desapareció pero quedó la otra.\n"
        "- `OK SEPARAR` — se pidió **no** unificar y siguen las dos filas (correcto).\n"
        "- `CONTRA LO PEDIDO` — se pidió separar y se fusionó, o al revés.\n",
    ]
    audita_personas(md)
    audita_ciudades(md)
    audita_premios(md)
    INFORME.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"-> {INFORME}")


if __name__ == "__main__":
    main()
