"""Etapa 12: Redes de participación: expositoras, instituciones, lugares y comisiones.

Objetivo de la versión anterior del formulario: "reconstruir redes de participación de
artesanas e instituciones". Las fuentes no registran vínculos entre personas; lo que sí dicen es
quién expuso, desde dónde, en qué concurso y quiénes organizaron. Con eso se arma un
grafo de cinco tipos de nodo (expositora, institución, lugar, concurso, comisión) y
estas aristas:

    participa         expositora/institución → concurso (peso = obras). Quien tiene
                      las dos es una expositora que repitió en 1915 y 1916
    procede           expositora/institución → lugar (peso = obras)
    organiza          integrante de la comisión → concurso (detalle = rol)
    es_expositora     integrante de la comisión → su registro de expositora
                      (`persona_id` en `comisiones.csv`)
    mismo_apellido    expositora ↔ expositora de la MISMA localidad con un apellido en común
                      (no cuentan los lugares "solo provincia").
                      Es una HIPÓTESIS de parentesco, no un dato: el detalle dice qué
                      apellido y de qué tipo ("propio = propio", "propio = de casada",
                      que sugiere madre e hija o suegra y nuera, "de casada = de casada")
    apellido_comision expositora ↔ integrante de la comisión con un apellido en común
                      (sin exigir lugar) que no sea frecuente: con López o Pérez la
                      coincidencia no dice nada. También hipótesis

`confianza` de las dos aristas de apellido: "baja" si el apellido es frecuente (lo
llevan 5 o más registros de la base), si no "media". Ninguna es "alta": confirmar un
parentesco pide otra fuente (prensa, registros civiles).

Apellidos: se sacan del nombre normalizado. Lo que va entre corchetes (variantes de
lectura) y los tratamientos (Sra., Srta., Sta.) se quitan; en "X de Y", Y es el
apellido de casada y la última palabra de X (si no es la de pila ni una inicial) el
propio; en registros conjuntos ("Concepción y Rosa Cuello") cuenta el apellido final.
Las instituciones no entran en las aristas de apellido.

Entrada : data/processed/tabla_normalizada.xlsx (Expositoras, Objetos, Ciudades,
          Concursos, Premios)
          data/interim/decisiones/comisiones.csv
Salida  : data/processed/redes.xlsx (hojas Nodos y Aristas, que se abren en Gephi o
          con networkx, y Grupos: las componentes conexas de `mismo_apellido`, que
          usa el explorador de `14`)
          outputs/redes.md (resumen: repetidoras, lugares, grupos por apellido,
          comisión)
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from itertools import combinations

import pandas as pd
from unidecode import unidecode

from _util import DECISIONES, PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
COMISIONES = DECISIONES / "comisiones.csv"
SALIDA = PROCESSED / "redes.xlsx"
INFORME = RAIZ / "outputs" / "redes.md"
FRECUENTE = 5  # registros con el mismo apellido a partir de los cuales la confianza baja

TRATAMIENTO = r"^(?:sra|srta|sta|señora|señorita)\.?\s+"


def clave(s: str) -> str:
    return unidecode(s).lower().strip()


def apellidos(nombre: str) -> dict[str, tuple[str, str]]:
    """{apellido normalizado: ("propio" | "de casada", apellido como se escribe)}."""
    s = re.sub(r"\[[^\]]*\]", " ", str(nombre))
    s = re.sub(TRATAMIENTO, "", s.strip(), flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    if " y " in s:  # registro conjunto: lo que va después de la última "y"
        s = s.rsplit(" y ", 1)[1]
    out: dict[str, str] = {}
    antes, _, despues = s.rpartition(" de ")
    if antes or s.lower().startswith("de "):
        casada = despues if antes else s[3:]
        casada = re.sub(r"^(?:la|los|las)\s+", "", casada.strip(), flags=re.I)
        if casada:
            out[clave(casada)] = ("de casada", casada)
            # compuesto ("Acuña Zavalía"): también la última palabra, como en el apellido propio
            ult = casada.split()[-1]
            if ult != casada and not re.fullmatch(r"[A-ZÁÉÍÓÚÑa-z]\.?", ult):
                out.setdefault(clave(ult), ("de casada", ult))
        s = antes
    palabras = [p for p in s.split() if not re.fullmatch(r"[A-ZÁÉÍÓÚÑa-z]\.?", p)]
    if len(palabras) >= 2:
        out.setdefault(clave(palabras[-1]), ("propio", palabras[-1]))
    return out


def tipo_par(a: str, b: str) -> str:
    return " = ".join(sorted([a, b], key=lambda t: t != "propio"))


def componentes(aristas: list[tuple[str, str]]) -> list[set[str]]:
    padre: dict[str, str] = {}

    def raiz(x):
        padre.setdefault(x, x)
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for a, b in aristas:
        padre[raiz(a)] = raiz(b)
    grupos = defaultdict(set)
    for x in padre:
        grupos[raiz(x)].add(x)
    return sorted(grupos.values(), key=len, reverse=True)


def tabla_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    filas = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        filas.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(filas)


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    E, O, C, K, P = (xl.parse(s) for s in ["Expositoras", "Objetos", "Ciudades", "Concursos", "Premios"])
    M = pd.read_csv(COMISIONES)
    anio = K.set_index("concurso_id")["anio"].to_dict()

    # lugar de cada ciudad: el nombre actual o, si no tiene, el del catálogo. No hace falta
    # que tenga coordenadas: la red no las usa, y Orán (24 obras) o Rosario quedaban
    # afuera sólo por estar sin ubicar. Lo que sólo dice la provincia ("TUCUMÁN", "Jujuy")
    # es un lugar "Catamarca (solo provincia)"; "S/d" no es ningún lugar (Julián, 30/10)
    nom = C["nombre_ciudad_hoy"].fillna(C["nombre_ciudad"])
    clave_prov = C["nombre_provincia"].map(lambda v: clave(str(v)) if pd.notna(v) else "")
    solo_prov = C["nombre_provincia"].notna() & (nom.isna() | (nom.map(lambda v: clave(str(v))) == clave_prov))
    sin_dato = ~solo_prov & (nom.isna() | nom.map(lambda v: clave(str(v)) in ("s/d", "sd")))
    C["lugar"] = nom.where(~solo_prov & ~sin_dato, C["nombre_provincia"] + " (solo provincia)").where(~sin_dato)
    lugar = C.set_index("ciudad_id")["lugar"].to_dict()
    solo_provincia = set(C.loc[solo_prov, "lugar"])
    prov = C.set_index("ciudad_id")["nombre_provincia"].to_dict()
    O["lugar"] = O["ciudad_id"].map(lugar)

    es_inst = E.set_index("persona_id")["Género"].eq("I").to_dict()
    nombre = E.set_index("persona_id")["Nombre"].to_dict()
    premios = P.dropna(subset=["persona_id"]).groupby("persona_id").size().to_dict()

    nodos, aristas = [], []
    nid = lambda pid: f"e{int(pid)}"  # noqa: E731

    for pid, g in O.groupby("expositora_id"):
        lugares = sorted(g["lugar"].dropna().unique())
        provs = sorted({prov[c] for c in g["ciudad_id"] if pd.notna(prov.get(c))})
        nodos.append({
            "id": nid(pid), "tipo": "institución" if es_inst.get(pid) else "expositora",
            "nombre": nombre.get(pid), "persona_id": int(pid),
            "concursos": ", ".join(str(anio[c]) for c in sorted(g["concurso_id"].unique())),
            "obras": len(g), "premios": premios.get(pid, 0),
            "lugar": "; ".join(lugares), "provincia": "; ".join(provs)})
        for c, n in g.groupby("concurso_id").size().items():
            aristas.append({"origen": nid(pid), "destino": f"k{anio[c]}", "tipo": "participa",
                            "peso": int(n), "detalle": "", "confianza": "dato"})
        for l, n in g.groupby("lugar").size().items():
            aristas.append({"origen": nid(pid), "destino": f"l:{l}", "tipo": "procede",
                            "peso": int(n), "detalle": "", "confianza": "dato"})

    for a in sorted(anio.values()):
        nodos.append({"id": f"k{a}", "tipo": "concurso", "nombre": f"Concurso de {a}"})
    for l, g in O.dropna(subset=["lugar"]).groupby("lugar"):
        nodos.append({"id": f"l:{l}", "tipo": "lugar", "nombre": l,
                      "provincia": prov.get(g["ciudad_id"].iloc[0]), "obras": len(g),
                      "expositoras": g["expositora_id"].nunique()})

    for n, g in M.groupby("nombre", sort=False):
        nodos.append({"id": f"m:{n}", "tipo": "comisión", "nombre": n,
                      "concursos": ", ".join(str(a) for a in sorted(g["anio"].unique()))})
        for _, r in g.iterrows():
            aristas.append({"origen": f"m:{n}", "destino": f"k{r.anio}", "tipo": "organiza",
                            "peso": 1, "detalle": r.rol, "confianza": "dato"})
        for pid in g["persona_id"].dropna().unique():
            aristas.append({"origen": f"m:{n}", "destino": nid(pid), "tipo": "es_expositora",
                            "peso": 1, "detalle": "", "confianza": "dato"})

    # ---- hipótesis por apellido
    personas = [p for p in E["persona_id"] if not es_inst.get(p)]
    ap = {p: apellidos(nombre[p]) for p in personas}
    frec = Counter(a for p in personas for a in ap[p])
    # sólo localidades: dos expositoras de "Catamarca (solo provincia)" no son de la misma
    # localidad, y unirlas por apellido sería inventar
    lugares_de = (O[O["lugar"].notna() & ~O["lugar"].isin(solo_provincia)]
                  .groupby("expositora_id")["lugar"].agg(set).to_dict())
    por_ap_lugar = defaultdict(set)
    for p in personas:
        for a in ap[p]:
            for l in lugares_de.get(p, ()):
                por_ap_lugar[(a, l)].add(p)
    vistos = set()
    for (a, l), ps in sorted(por_ap_lugar.items()):
        for x, y in combinations(sorted(ps), 2):
            if (x, y, a) in vistos:
                continue
            vistos.add((x, y, a))
            aristas.append({"origen": nid(x), "destino": nid(y), "tipo": "mismo_apellido",
                            "peso": 1, "detalle": f"{ap[x][a][1]} ({tipo_par(ap[x][a][0], ap[y][a][0])}), {l}",
                            "confianza": "baja" if frec[a] >= FRECUENTE else "media"})
    for n in M["nombre"].unique():
        for a in apellidos(n):
            for p in personas:
                if (a in ap[p] and frec[a] < FRECUENTE
                        and p not in set(M.loc[M["nombre"] == n, "persona_id"].dropna())):
                    aristas.append({"origen": f"m:{n}", "destino": nid(p), "tipo": "apellido_comision",
                                    "peso": 1, "detalle": ap[p][a][1], "confianza": "media"})

    N, A = pd.DataFrame(nodos), pd.DataFrame(aristas)
    for col in ["persona_id", "obras", "premios", "expositoras"]:
        N[col] = N[col].astype("Int64")
    G = grupos(N, A)
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        N.to_excel(w, sheet_name="Nodos", index=False)
        A.to_excel(w, sheet_name="Aristas", index=False)
        G.to_excel(w, sheet_name="Grupos", index=False)
    print(f"{len(N)} nodos, {len(A)} aristas: {A['tipo'].value_counts().to_dict()}; {len(G)} grupos")
    print(f"-> {SALIDA}")
    informe(N, A, G)


def grupos(N: pd.DataFrame, A: pd.DataFrame) -> pd.DataFrame:
    """Componentes conexas de `mismo_apellido`: cada grupo con sus apellidos, lugares,
    confianza (media si algún apellido del grupo es poco frecuente) e integrantes."""
    nom = N.set_index("id")["nombre"].to_dict()
    fam = A[A["tipo"] == "mismo_apellido"]
    filas = []
    for i, g in enumerate(componentes(list(zip(fam["origen"], fam["destino"]))), 1):
        sub = fam[fam["origen"].isin(g)]
        ids = sorted(g, key=lambda x: nom[x])
        filas.append({
            "grupo": i, "personas": len(g),
            "apellidos": ", ".join(sorted({d.split(" (")[0] for d in sub["detalle"]})),
            "lugar": ", ".join(sorted({d.rsplit(", ", 1)[1] for d in sub["detalle"]})),
            "confianza": "media" if (sub["confianza"] == "media").any() else "baja",
            "persona_ids": ";".join(x[1:] for x in ids),
            "integrantes": "; ".join(nom[x] for x in ids)})
    return pd.DataFrame(filas)


def informe(N: pd.DataFrame, A: pd.DataFrame, G: pd.DataFrame) -> None:
    ex = N[N["tipo"].isin(["expositora", "institución"])].copy()
    nom = N.set_index("id")["nombre"].to_dict()
    rep = ex[ex["concursos"] == "1915, 1916"].sort_values(["obras", "nombre"], ascending=[False, True])
    lug = N[N["tipo"] == "lugar"].sort_values(["expositoras", "obras"], ascending=False)
    proc = A[A["tipo"] == "procede"]
    rep_l = proc[proc["origen"].isin(rep["id"])].groupby("destino")["origen"].nunique()
    lug = lug.assign(repiten=lug["id"].map(rep_l).fillna(0).astype(int))

    fam = A[A["tipo"] == "mismo_apellido"]
    madre = fam[fam["detalle"].str.contains(r"propio = de casada")]
    com = A[A["tipo"] == "apellido_comision"]

    t = ["# Redes de participación", "",
         "Generado por `src/pipeline/12_redes.py` en cada corrida. Las aristas de apellido "
         "son **hipótesis de parentesco**, no datos: sirven para orientar la búsqueda en "
         "otras fuentes. El grafo completo está en `data/processed/redes.xlsx`.", "",
         "## Resumen", "",
         f"- {len(ex)} registros de expositoras ({(ex['tipo'] == 'institución').sum()} instituciones), "
         f"{len(lug)} lugares, {(N['tipo'] == 'comisión').sum()} integrantes de comisión.",
         f"- **{len(rep)} expositoras expusieron en los dos concursos** "
         f"({100 * len(rep) / len(ex):.0f} % de los registros).",
         f"- {len(fam)} pares con apellido en común en el mismo lugar, que forman "
         f"{len(G)} grupos ({(G['confianza'] == 'media').sum() if len(G) else 0} con algún "
         f"apellido poco frecuente). De esos pares, {len(madre)} combinan apellido propio con "
         f"apellido de casada (¿madre e hija, suegra y nuera?).",
         f"- {len(com)} coincidencias de apellido entre la comisión y las expositoras.", "",
         "## Expositoras que repitieron (1915 y 1916)", "",
         tabla_md(rep[["nombre", "lugar", "obras", "premios"]].rename(columns=str.capitalize)), "",
         "## Lugares", "",
         "Expositoras distintas por lugar y cuántas de ellas expusieron en los dos concursos.", "",
         tabla_md(lug[["nombre", "provincia", "expositoras", "repiten", "obras"]].head(20)
                  .rename(columns=str.capitalize)), "",
         "## Grupos por apellido y lugar (hipótesis)", "",
         "Componentes conexas de la arista `mismo_apellido`. Confianza baja = todos los "
         f"apellidos del grupo los llevan {FRECUENTE} o más registros.", "",
         tabla_md(G.drop(columns=["grupo", "persona_ids"]).head(30).rename(columns=str.capitalize))
         if len(G) else "Ninguno.", "",
         "## Comisión y expositoras con apellido en común (hipótesis)", "",
         tabla_md(com.assign(Comisión=com["origen"].map(nom), Expositora=com["destino"].map(nom))
                  [["Comisión", "Expositora", "detalle"]].rename(columns={"detalle": "Apellido"}))
         if len(com) else "Ninguna.", ""]
    INFORME.write_text("\n".join(t), encoding="utf-8")
    print(f"-> {INFORME}")


if __name__ == "__main__":
    main()
