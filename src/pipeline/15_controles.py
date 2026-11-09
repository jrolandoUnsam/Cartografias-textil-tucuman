"""Etapa 15: Controles de calidad de la base.

Busca, en toda la tabla normalizada, los errores típicos de transcribir catálogos de
1915-1916 (`docs/bitacora.md`, 2026-10-28): personas escritas distinto, lugares
ambiguos, números de orden repetidos o fuera de su página, premios que no cierran y
erratas. No corrige nada: lista los casos para revisarlos.

Cada control dice cuántos casos hay y cuáles son, con su id y la página escaneada para
ir a la fuente. Lo ya decidido (pares marcados "no se unen", fusiones aplicadas, las
6 filas de dos personas) no vuelve a aparecer como caso abierto.

Entrada : data/processed/tabla_normalizada.xlsx
          data/interim/objetos_crudos.csv (cómo lo escribió el catálogo)
          data/interim/duplicados_expositoras_candidatos.xlsx
Salida  : outputs/controles_calidad.md
"""
from __future__ import annotations

import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz
from unidecode import unidecode

from _util import INTERIM, PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
CRUDOS = INTERIM / "objetos_crudos.csv"
CANDIDATOS = INTERIM / "duplicados_expositoras_candidatos.xlsx"
SALIDA = RAIZ / "outputs" / "controles_calidad.md"

# pares de `pares_sin_revisar.xlsx` (25/10) que LM no contestó; ver docs/tareas_pendientes.md
ENVIADOS_LM = {frozenset(p) for p in [(2, 45), (390, 409), (215, 474), (129, 176), (466, 468), (435, 506), (325, 334)]}
# filas de dos personas que LM decidió dejar como registro conjunto (2026-10-28)
CONJUNTOS = {25, 104, 341, 390, 399, 471}
PALABRAS_INSTITUCION =r"\b(?:asilo|escuela|colegio|hermanas|superiora|sociedad|patronato|taller|instituto|mision|convento|hogar|liceo|congregacion)\b"


def clave(s) -> str:
    return re.sub(r"\s+", " ", unidecode(str(s or "")).lower()).strip() if pd.notna(s) else ""


def num(v):
    try:
        return int(float(str(v).strip()))
    except ValueError:
        return None


class Informe:
    def __init__(self):
        self.secciones, self.resumen = [], []

    def control(self, grupo, titulo, explica, filas, columnas, accion):
        self.resumen.append((grupo, titulo, len(filas), accion))
        md = [f"### {titulo}", "", explica, ""]
        if filas:
            md += ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
            md += ["| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in f) + " |" for f in filas]
        else:
            md.append("Ningún caso.")
        self.secciones.append((grupo, "\n".join(md) + "\n"))
        print(f"  {len(filas):4d}  {titulo}")

    def escribir(self):
        out = ["# Controles de calidad de la base", "",
               "Generado por `src/pipeline/15_controles.py` en cada corrida del pipeline. "
               "Lista casos para revisar; no corrige nada. Las páginas (DSCN…) son los escaneos "
               "del catálogo o del fallo.", "",
               "## Resumen", "", "| Grupo | Control | Casos | Qué hacer |", "|---|---|--:|---|"]
        out += [f"| {g} | {t} | {n} | {a} |" for g, t, n, a in self.resumen]
        grupo = None
        for g, md in self.secciones:
            if g != grupo:
                out += ["", f"## {g}", ""]
                grupo = g
            out.append(md)
        SALIDA.write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E, O, C = xl.parse("Expositoras"), xl.parse("Objetos"), xl.parse("Ciudades")
    K, Cat, Pr, Pg = xl.parse("Concursos"), xl.parse("Categorías"), xl.parse("Premios"), xl.parse("Paginas_Catalogo")
    Pr = Pr.rename(columns={"Nombre en el fallo": "nf", "Ciudad en el fallo": "cf", "Sección del fallo": "sf",
                            "Objeto en el fallo": "of", "N.º": "numf"})
    crudo = pd.read_csv(CRUDOS).set_index("objeto_id")
    anio = K.set_index("concurso_id")["anio"]
    O["anio"] = O["concurso_id"].map(anio)
    O["cat"] = O["categoria_id"].map(Cat.set_index("categoria_id")["nombre_categoria"])
    O["lugar_doc"] = O["objeto_id"].map(crudo["ciudad_raw"])
    nombre = E.set_index("persona_id")["Nombre"]
    genero = E.set_index("persona_id")["Género"]
    Ci = C.set_index("ciudad_id")
    O["prov"] = O["ciudad_id"].map(Ci["nombre_provincia"])
    O["ciudad"] = O["ciudad_id"].map(Ci["nombre_ciudad"])
    obras = O.groupby("expositora_id").size()
    inf = Informe()

    # ------------------------------------------------------------------ personas
    G = "Personas"
    cand = pd.read_excel(CANDIDATOS)
    vivos = set(E["persona_id"])
    sin_anotar = cand[(cand["ya_fusionada"] != True) & cand["Hecho"].isna()  # noqa: E712
                      & cand["id_A"].isin(vivos) & cand["id_B"].isin(vivos)]
    par = lambda r: frozenset((int(r.id_A), int(r.id_B)))  # noqa: E731
    abiertos = [r for r in sin_anotar.itertuples() if par(r) in ENVIADOS_LM]
    inf.control(G, "Nombres parecidos que esperan respuesta de LM",
                "Pares del detector de duplicados (`02_candidatos`) que se le mandaron a LM y no contestó. Los otros "
                f"{len(sin_anotar) - len(abiertos)} pares sin anotar son los que Julián dio por personas distintas el "
                "25/10 (mismo apellido, otro nombre de pila) y no se listan.",
                [(int(r.id_A), nombre[r.id_A], int(r.id_B), nombre[r.id_B], f"{r.score:.0f}") for r in abiertos],
                ["id A", "Nombre A", "id B", "Nombre B", "Parecido"], "Volver a preguntarle a LM o darlos por distintos")

    E["k"] = E["Nombre"].map(clave)
    rep = E[E["k"].duplicated(keep=False)].sort_values("k")
    inf.control(G, "Mismo nombre, dos registros",
                "Nombres idénticos (sin contar tildes ni mayúsculas) con distinto id: o falta unirlos o son "
                "homónimas que se decidió mantener separadas.",
                [(int(r.persona_id), r.Nombre, int(obras.get(r.persona_id, 0))) for r in rep.itertuples()],
                ["id", "Nombre", "Obras"], "Confirmar que la separación es a propósito")

    sin_pila = E[E["k"].str.match(r"^(?:sra|senora|sta|srta|dona|de)\b")]
    inf.control(G, "Sin nombre de pila",
                "Registradas sólo como \"Sra. de…\" o \"Sta. …\": difíciles de unir con otras apariciones de la misma "
                "persona. \"Sta.\" puede ser señorita o Santa.",
                [(int(r.persona_id), r.Nombre, int(obras.get(r.persona_id, 0))) for r in sin_pila.itertuples()],
                ["id", "Nombre", "Obras"], "Buscar el nombre completo en el fallo o la prensa")

    # "e" seguida de punto es una inicial (María E. Pereyra), no una conjunción
    dos = E[E["k"].str.contains(r"\b(?:y|e)\b(?!\.)") & ~E["k"].str.contains(PALABRAS_INSTITUCION)]
    nuevos = dos[~dos["persona_id"].isin(CONJUNTOS)]
    inf.control(G, "Dos personas en un registro",
                "Nombres con \"y\" / \"e\" que no son instituciones. Los 6 conocidos (Cuello, Díaz y Bazán, Gramajo, "
                "Gómez, Blay, Vivolo y Cerrasuolo) quedan como registro conjunto (LM 2026-10-28) y no se listan.",
                [(int(r.persona_id), r.Nombre, int(obras.get(r.persona_id, 0))) for r in nuevos.itertuples()],
                ["id", "Nombre", "Obras"], "Decidir si se separan")

    inst = E[E["k"].str.contains(PALABRAS_INSTITUCION) & (E["Género"] != "I")]
    inf.control(G, "Parece institución pero tiene género de persona",
                "El nombre menciona una escuela, asilo, colegio… y no lleva `I`. Puede ser una persona de esa "
                "institución (\"Mamerta Monteros [Escuela Sarmiento 1915]\").",
                [(int(r.persona_id), r.Nombre, r.Género) for r in inst.itertuples()],
                ["id", "Nombre", "Género"], "Decidir si es persona o institución")

    raro = E[~E["Género"].isin(["F", "M", "I"])]
    inf.control(G, "Género vacío o desconocido", "Valores fuera de F / M / I.",
                [(int(r.persona_id), r.Nombre, r.Género) for r in raro.itertuples()], ["id", "Nombre", "Género"],
                "Completar en `nombres_expositoras.csv`")

    abrev = E[E["Nombre"].str.contains(r"[?()]")]
    inf.control(G, "Signos de duda en el nombre",
                "Un \"?\" o un paréntesis indica una lectura dudosa. (Los corchetes son variantes ya acordadas con LM.)",
                [(int(r.persona_id), r.Nombre) for r in abrev.itertuples()], ["id", "Nombre"], "Revisar contra el escaneo")

    # ------------------------------------------------------------------ lugares
    G = "Lugares"
    solo = C["nombre_provincia"].notna() & (C["nombre_ciudad"].isna() | (C["nombre_ciudad"].map(clave) == C["nombre_provincia"].map(clave)))
    solo_ids = set(C.loc[solo, "ciudad_id"])
    filas = []
    for pid, g in O.groupby("expositora_id"):
        for cid in set(g["ciudad_id"]) & solo_ids:
            otras = sorted({Ci.at[c, "nombre_ciudad"] for c in g["ciudad_id"] if c not in solo_ids and Ci.at[c, "nombre_provincia"] == Ci.at[cid, "nombre_provincia"]})
            if otras:
                filas.append((int(pid), nombre[pid], Ci.at[cid, "nombre_provincia"], ", ".join(otras)))
    movidas = O["ciudad_id_catalogo"].notna().sum() if "ciudad_id_catalogo" in O.columns else 0
    inf.control(G, "Sólo provincia con una localidad de la misma expositora",
                f"Obras con sólo la provincia cuando la misma expositora tiene una localidad en esa provincia. "
                f"`06` ya pasó {movidas} obras a su localidad; acá quedan las que no pudo resolver (dos localidades posibles).",
                filas, ["id", "Expositora", "Provincia", "Localidades"], "Elegir la localidad a mano")

    sin_coord = C[C["lat"].isna() & ~solo]
    n_obras_c = O.groupby("ciudad_id").size()
    inf.control(G, "Localidades sin coordenadas",
                "Lugares que el mapa no puede ubicar en su punto (van al de la provincia, o a ninguno).",
                [(int(r.ciudad_id), r.nombre_ciudad, r.nombre_provincia if pd.notna(r.nombre_provincia) else "s/d",
                  int(n_obras_c.get(r.ciudad_id, 0)), r.nota if pd.notna(r.nota) else "") for r in sin_coord.itertuples()],
                ["id", "Lugar", "Provincia", "Obras", "Nota"], "Ubicar o dejar como desconocida")

    dudosa = C[(C["precision"] == "tentativa") | C["nombre_ciudad_hoy"].astype(str).str.contains(r"\?| o ", regex=True)]
    inf.control(G, "Ubicaciones tentativas o ambiguas",
                "Coordenadas marcadas `tentativa` o nombre actual con \"?\" u \"o\" (dos candidatas).",
                [(int(r.ciudad_id), r.nombre_ciudad, r.nombre_ciudad_hoy, r.nombre_provincia, r.nota if pd.notna(r.nota) else "") for r in dudosa.itertuples()],
                ["id", "En el catálogo", "Hoy", "Provincia", "Nota"], "Confirmar con LM o con fuentes")

    C["kh"] = C["nombre_ciudad_hoy"].map(clave)
    hom = C[C["kh"].ne("") & C["kh"].duplicated(keep=False)].sort_values("kh")
    inf.control(G, "Varios lugares del catálogo, una misma localidad actual",
                "Ids distintos que hoy son el mismo lugar (p. ej. dos ingenios en Banda del Río Salí). "
                "Puede ser a propósito (se conserva cómo lo escribió el catálogo) o una fusión pendiente.",
                [(int(r.ciudad_id), r.nombre_ciudad, r.nombre_ciudad_hoy, int(n_obras_c.get(r.ciudad_id, 0))) for r in hom.itertuples()],
                ["id", "En el catálogo", "Hoy", "Obras"], "Confirmar que la separación es a propósito")

    filas = []
    for pid, g in O.groupby("expositora_id"):
        provs = sorted(set(g["prov"].dropna()))
        if len(provs) > 1:
            filas.append((int(pid), nombre[pid], "; ".join(f"{p} ({', '.join(sorted(set(g.loc[g.prov == p, 'ciudad'].fillna(p))))})" for p in provs),
                          ", ".join(map(str, sorted(set(g["anio"]))))))
    inf.control(G, "Expositora en dos provincias",
                "La misma persona con obras de provincias distintas: puede haberse mudado, o la fusión unió a dos personas distintas.",
                filas, ["id", "Expositora", "Lugares", "Años"], "Revisar la fusión")

    filas = []
    for pid, g in O[~O["ciudad_id"].isin(solo_ids)].groupby("expositora_id"):
        cs = sorted(set(g["ciudad"].dropna()))
        if len(cs) > 1 and len(set(g["prov"].dropna())) == 1:
            filas.append((int(pid), nombre[pid], ", ".join(cs), ", ".join(map(str, sorted(set(g["anio"]))))))
    inf.control(G, "Expositora en varias localidades de una provincia",
                "Puede ser real (vivía en un lugar y envió desde otro, o el catálogo nombra el departamento en un año y el pueblo en otro).",
                filas, ["id", "Expositora", "Localidades", "Años"], "Revisar si es el mismo lugar escrito distinto")

    # ------------------------------------------------------------------ números y páginas
    G = "Números de orden y páginas"
    rep = O[O.duplicated(["concurso_id", "categoria_id", "ORDEN"], keep=False)].sort_values(["anio", "cat", "ORDEN"])
    inf.control(G, "N.º de orden repetido en la misma sección",
                "Dos obras con el mismo número en la misma sección y concurso: error de transcripción o fila duplicada.",
                [(r.anio, r.cat, r.ORDEN, int(r.objeto_id), nombre.get(r.expositora_id), r.OBJETO, r.imagen) for r in rep.itertuples()],
                ["Año", "Sección", "N.º", "objeto_id", "Expositora", "Obra", "Página"], "Corregir contra el escaneo")

    filas = []
    for (a, c), g in O.groupby(["anio", "cat"]):
        ns = sorted(set(g["ORDEN"]))
        falta = sorted(set(range(ns[0], ns[-1] + 1)) - set(ns))
        if falta:
            filas.append((a, c, f"{ns[0]}–{ns[-1]}", ", ".join(map(str, falta))))
    inf.control(G, "Huecos en la numeración de una sección",
                "Números que faltan entre el primero y el último de una sección: obra sin transcribir, número mal leído, o "
                "un salto del propio catálogo.",
                filas, ["Año", "Sección", "Rango", "Faltan"], "Mirar el escaneo de esa sección")

    filas = []
    rangos = Pg.dropna(subset=["orden_desde", "orden_hasta"])
    por_img = defaultdict(list)
    for r in rangos.itertuples():
        por_img[r.imagen].append((int(r.orden_desde), int(r.orden_hasta), clave(r.categoria_o_seccion)))
    for r in O.itertuples():
        rs = por_img.get(r.imagen)
        if rs and not any(d <= r.ORDEN <= h for d, h, _ in rs):
            filas.append((r.anio, r.cat, r.ORDEN, int(r.objeto_id), nombre.get(r.expositora_id), r.imagen, "; ".join(f"{d}–{h}" for d, h, _ in rs)))
    inf.control(G, "N.º fuera del rango de su página",
                "El número de la obra no cae entre el primero y el último de la página escaneada que tiene asignada "
                "(`Paginas_Catalogo`): la página o el número están mal.",
                filas, ["Año", "Sección", "N.º", "objeto_id", "Expositora", "Página", "Rango de la página"], "Corregir página o número")

    # el índice de páginas anota quién abre y quién cierra cada sección de cada página.
    # Se ordena por objeto_id (el orden impreso), no por N.º: Pañuelos 1915 imprime
    # 16, 19, 18 (DSCN5177) y la última de la página es la del 18
    filas = []
    O["kcat"] = O["cat"].map(clave)
    for r in Pg.dropna(subset=["orden_desde", "orden_hasta"]).itertuples():
        o = O[(O["imagen"] == r.imagen) & O["ORDEN"].between(r.orden_desde, r.orden_hasta)
              & (O["kcat"].str[:6] == clave(r.categoria_o_seccion)[:6])].sort_values("objeto_id")
        if o.empty:
            continue
        for lado, quien, ob in (("primera", r.primera_persona, o.iloc[0]), ("última", r.ultima_persona, o.iloc[-1])):
            escrito = crudo.at[ob.objeto_id, "nombre_raw"]
            if pd.notna(quien) and fuzz.token_sort_ratio(clave(quien), clave(escrito)) < 85 and "?" not in str(escrito):
                filas.append((r.imagen, f"{r.pagina_impresa:.0f}" if pd.notna(r.pagina_impresa) else "", r.categoria_o_seccion,
                              lado, quien, ob.ORDEN, escrito))
    inf.control(G, "El índice de páginas no coincide con las obras",
                "`Paginas_Catalogo` dice quién abre y quién cierra cada sección en cada página; acá no coincide con la obra de "
                "ese número. Suele ser un número de orden mal transcripto o dos obras invertidas.",
                filas, ["Página", "Pág. impresa", "Sección", "Lugar", "Según el índice", "N.º", "Según la transcripción"],
                "Mirar el escaneo y corregir el número o el índice")

    por_anio = O.groupby("cat")["anio"].agg(lambda s: sorted(set(s)))
    solo_un = [(c, a[0], int((O["cat"] == c).sum())) for c, a in por_anio.items() if len(a) == 1]
    inf.control(G, "Secciones que existen en un solo concurso",
                "Nombres de sección que no se repiten entre 1915 y 1916 (\"Tejidos varios\" / \"Tejidos en general\"): "
                "falta decidir cómo se comparan (`categoria_norm`).",
                sorted(solo_un, key=lambda f: (f[1], f[0])), ["Sección", "Año", "Obras"], "Decidir la unificación de categorías")

    # ------------------------------------------------------------------ premios
    G = "Premios"
    obj = O.set_index("objeto_id")
    pr_obj = []
    for r in Pr.itertuples():
        for x in re.split(r"[;,]", str(r.objeto_id)) if pd.notna(r.objeto_id) else []:
            if num(x) is not None:
                pr_obj.append((r, num(x)))
    filas = [(int(r.premio_id), r.nf, nombre.get(r.persona_id, "") if pd.notna(r.persona_id) else "", oid,
              nombre.get(obj.at[oid, "expositora_id"]) if oid in obj.index else "no existe")
             for r, oid in pr_obj if oid not in obj.index or (pd.notna(r.persona_id) and obj.at[oid, "expositora_id"] != r.persona_id)]
    inf.control(G, "La expositora del premio no es la de la obra",
                "El premio apunta a una persona y a una obra de otra persona (o a una obra que no existe).",
                filas, ["premio_id", "Nombre en el fallo", "persona_id del premio", "objeto_id", "Expositora de la obra"], "Corregir el vínculo")

    cuenta = defaultdict(list)
    for r, oid in pr_obj:
        cuenta[oid].append(r)
    filas = [(oid, nombre.get(obj.at[oid, "expositora_id"]), obj.at[oid, "OBJETO"],
              "; ".join(f"{int(r.premio_id)}: {r.Premio}" for r in rs)) for oid, rs in cuenta.items() if len(rs) > 1 and oid in obj.index]
    inf.control(G, "Obra con más de un premio",
                "Puede ser real (premio y accésit) o dos premios del fallo vinculados a la misma pieza por error (el caso de la blusa).",
                filas, ["objeto_id", "Expositora", "Obra", "Premios"], "Confirmar")

    filas = [(int(r.premio_id), r.nf, oid, obj.at[oid, "OBJETO"]) for r, oid in pr_obj
             if oid in obj.index and str(obj.at[oid, "fuera_de_concurso"]) == "sí"]
    inf.control(G, "Premio a una obra fuera de concurso",
                "Contradicción: el catálogo dice que la obra no competía.", filas,
                ["premio_id", "Nombre en el fallo", "objeto_id", "Obra"], "Revisar vínculo o marca")

    filas = []
    for r, oid in pr_obj:
        a, b = num(r.numf), (obj.at[oid, "ORDEN"] if oid in obj.index else None)
        if a is not None and b is not None and a != b:
            filas.append((int(r.premio_id), r.nf, r.sf, a, oid, b, r.Vínculo))
    inf.control(G, "N.º del fallo distinto del N.º del catálogo",
                "El fallo cita un número y la obra vinculada tiene otro. A veces es a propósito (vínculo por nombre), a veces "
                "un error de uno de los dos documentos.",
                filas, ["premio_id", "Nombre en el fallo", "Sección del fallo", "N.º fallo", "objeto_id", "N.º catálogo", "Vínculo"], "Revisar")

    def variantes(n):
        """'Lugarda [Lujarda] J. de González' -> sin corchetes, y con la variante en lugar de la
        palabra anterior. Si el corchete tiene dos palabras o más, también sólo lo de adentro:
        'Colegio de la Sagrada Familia [Mercedes Pacheco]' -> 'Mercedes Pacheco' (como 07_premios)."""
        n = str(n)
        lecturas = {re.sub(r"\s*\[[^]]*\]", "", n), re.sub(r"\S+\s*\[([^]]*)\]", r"\1", n)}
        lecturas |= {d for d in re.findall(r"\[([^]]*)\]", n) if len(d.split()) >= 2}
        return lecturas

    filas = []
    for r in Pr.itertuples():
        if pd.notna(r.persona_id):
            fallo = clave(re.sub(r"[()]", "", str(r.nf)))
            s = max(fuzz.token_sort_ratio(fallo, clave(v)) for v in variantes(nombre.get(r.persona_id, "")))
            if s < 80:
                filas.append((int(r.premio_id), r.nf, nombre.get(r.persona_id, ""), f"{s:.0f}"))
    inf.control(G, "Nombre del fallo muy distinto del catálogo",
                "El fallo y el catálogo escriben a la persona de forma muy diferente: confirmar que es la misma.",
                filas, ["premio_id", "Nombre en el fallo", "En la base", "Parecido"], "Confirmar la identidad")

    filas = []
    for r, oid in pr_obj:
        if oid not in obj.index or pd.isna(r.cf):
            continue
        f = clave(r.cf)
        cid = obj.at[oid, "ciudad_id_catalogo"] if pd.notna(obj.at[oid, "ciudad_id_catalogo"]) else obj.at[oid, "ciudad_id"]
        c, p = clave(Ci.at[cid, "nombre_ciudad"]), clave(Ci.at[cid, "nombre_provincia"])
        if f in ("", "s/d") or ("ciudad" in f and c == "san miguel de tucuman"):
            continue
        if f not in (c, p) and f not in c and c not in f and fuzz.ratio(f, c) < 80:
            filas.append((int(r.premio_id), r.nf, r.cf, oid, Ci.at[cid, "nombre_ciudad"] if pd.notna(Ci.at[cid, "nombre_ciudad"]) else Ci.at[cid, "nombre_provincia"]))
    inf.control(G, "Lugar del fallo distinto del catálogo",
                "El fallo ubica a la premiada en otro lugar que el catálogo: o la obra vinculada es otra, o uno de los documentos se equivoca.",
                filas, ["premio_id", "Nombre en el fallo", "Lugar en el fallo", "objeto_id", "Lugar en el catálogo"], "Revisar")

    # el nombre sin puntos ni "de": "Lujarda J. de González" = "Lujarda J Gonzalez"
    sin_de = Pr["nf"].map(clave).str.replace(r"[^a-z ]", " ", regex=True).str.replace(r"de", " ", regex=True).str.split().str.join(" ")
    Pr["kp"] = sin_de + "|" + Pr["sf"].map(clave) + "|" + Pr["Premio"].map(clave) + "|" + Pr["of"].map(clave) + "|" + Pr["numf"].map(clave)
    rep = Pr[Pr["kp"].duplicated(keep=False)].sort_values("kp")
    inf.control(G, "Premio repetido en el fallo",
                "Mismo nombre, sección, premio, objeto y N.º en dos filas: el fallo premió dos piezas iguales o la fila se "
                "transcribió dos veces.",
                [(int(r.premio_id), r.nf, r.Premio, r.sf, r.of if pd.notna(r.of) else "", r.objeto_id if pd.notna(r.objeto_id) else "") for r in rep.itertuples()],
                ["premio_id", "Nombre en el fallo", "Premio", "Sección", "Objeto en el fallo", "objeto_id"], "Revisar contra el fallo")

    sin = Pr[Pr["objeto_id"].isna() | (Pr["objeto_id"].astype(str).str.strip() == "")]
    inf.control(G, "Premios sin obra en el catálogo",
                "Fuera de catálogo o pendientes de vincular (informativo).",
                [(int(r.premio_id), r.nf, r.Premio, r.sf, r.of if pd.notna(r.of) else "", r.Estado) for r in sin.itertuples()],
                ["premio_id", "Nombre en el fallo", "Premio", "Sección", "Objeto en el fallo", "Estado"], "Nada, salvo los pendientes")

    # ------------------------------------------------------------------ transcripción
    G = "Transcripción"
    O["ko"] = O["OBJETO"].map(clave)
    corta = O[O["ko"].str.len() < 4]
    inf.control(G, "Descripción vacía o muy corta", "Obras sin texto o con menos de 4 letras.",
                [(int(r.objeto_id), r.anio, r.cat, r.ORDEN, nombre.get(r.expositora_id), r.OBJETO, r.imagen) for r in corta.itertuples()],
                ["objeto_id", "Año", "Sección", "N.º", "Expositora", "Obra", "Página"], "Completar desde el escaneo")

    marca = O[O["OBJETO"].astype(str).str.contains(r"\?|\[|s/d|ilegible", case=False, regex=True)]
    inf.control(G, "Lecturas dudosas en la descripción",
                "Textos con \"?\", corchetes, \"s/d\" o \"ilegible\": quien transcribió no estaba seguro.",
                [(int(r.objeto_id), r.anio, r.cat, r.ORDEN, nombre.get(r.expositora_id), r.OBJETO, r.imagen) for r in marca.itertuples()],
                ["objeto_id", "Año", "Sección", "N.º", "Expositora", "Obra", "Página"], "Revisar contra el escaneo")

    lug = O[O["lugar_doc"].astype(str).str.contains(r"\?|\(|s/d", case=False, regex=True)]
    inf.control(G, "Lecturas dudosas en el lugar",
                "El lugar transcripto tiene \"?\", paréntesis o \"s/d\".",
                [(int(r.objeto_id), r.anio, nombre.get(r.expositora_id), r.lugar_doc, r.ciudad if pd.notna(r.ciudad) else r.prov, r.imagen) for r in lug.itertuples()],
                ["objeto_id", "Año", "Expositora", "Lugar en el documento", "Lugar en la base", "Página"], "Revisar")

    sin_img = O[O["imagen"].isna()]
    inf.control(G, "Obras sin página escaneada", "No se puede ir a la fuente.",
                [(int(r.objeto_id), r.anio, r.cat, r.ORDEN, nombre.get(r.expositora_id)) for r in sin_img.itertuples()],
                ["objeto_id", "Año", "Sección", "N.º", "Expositora"], "Asignar página")

    inf.escribir()
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
