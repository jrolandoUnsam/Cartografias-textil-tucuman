"""Etapa 05c — Explorador web (mapa, técnicas por zona, expositoras).

Llena la plantilla `plantillas/explorador.template.html` con los datos de la tabla
normalizada y escribe `outputs/explorador.html`: un único archivo, sin servidor, que
se abre en el navegador. La plantilla es el diseño del explorador; acá sólo se arma el
JSON que consume (`DATA`) y se pega el CSS de Leaflet (también en `plantillas/`). El mapa base es Esri
World Street Map, como en `05b_mapa`, y se carga de internet al abrir la página
(tile.openstreetmap.org se bloquea si la página se abre como archivo local).

Una obra = una fila de `Objetos` (981). A eso se suman, como obras aparte, los premios
de 1915 que no tienen objeto en el catálogo (hoja `Premios`, que arma `04e`, sin
`objeto_id`): el fallo los premia pero no figuran en el listado de expositoras.

Lo que no sale de la tabla y es decisión del proyecto vive en `decisiones/`:

  familias_categorias.csv   por categoría: `familia` (tipo de obra) y
                            `tecnica_por_categoria`, la técnica que se asume cuando el
                            texto del objeto no menciona ninguna
  zonas_ciudades.csv        zona de cada `ciudad_id`. Propuesta inicial armada por
                            provincia y distancia a la capital (columna `criterio`);
                            se edita a mano

Las técnicas se infieren del texto del objeto con las reglas de `REGLAS_TECNICA`. Si
no hay ninguna, se usa la de la categoría (`ts = "c"`); si tampoco, queda "sin técnica
indicada" (`ts = "n"`).

Lugares: un círculo por punto (`lat`/`lon` redondeados a ~100 m), así "La Cocha" y
"Escuela de la Cocha" o "Asilo Ciudad" y San Miguel van juntos. Lo que no tiene punto
de ciudad pero sí provincia se agrupa en un lugar "sólo provincia" en la capital, como
en `05b_mapa`. Lo que no tiene ninguno de los dos queda sin coordenadas: se lista en
la matriz y en las fichas, no en el mapa.

Entrada : data/processed/tabla_normalizada.xlsx (Objetos, Expositoras, Categorías,
          Ciudades, Premios), data/interim/objetos_crudos.csv (nombre tal como figura
          en el catálogo), decisiones/*.csv
Salida  : outputs/explorador.html
"""
from __future__ import annotations

import json
import re
from collections import Counter

import pandas as pd
from unidecode import unidecode

from _util import DECISIONES, INTERIM, PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
CRUDOS = INTERIM / "objetos_crudos.csv"
FAMILIAS = DECISIONES / "familias_categorias.csv"
ZONAS = DECISIONES / "zonas_ciudades.csv"
PLANTILLAS = RAIZ / "src" / "pipeline" / "plantillas"
SALIDA = RAIZ / "outputs" / "explorador.html"

SEDE_CIUDAD = 2  # San Miguel de Tucumán: sede de los dos concursos

FAM = {"tej": "Tejidos de telar y abrigo", "alf": "Alfombras y tapices",
       "enc": "Encajes, randas y crochet", "bor": "Bordados y deshilados", "otr": "Otros"}
TEC = {"randa": "Randa", "encaje": "Encaje", "filet": "Filet", "crochet": "Crochet e irlanda",
       "deshilado": "Deshilado", "bordado": "Bordado", "telar": "Telar",
       "pala": "A pala o a bastones", "encrand": "Encaje o randa (sin precisar)",
       "bordesh": "Bordado o deshilado (sin precisar)", "sin": "Sin técnica indicada"}
ZON = {"cap": "Capital y alrededores", "tcs": "Centro y sur de Tucumán",
       "tvn": "Valles y norte de Tucumán", "tsl": "Tucumán, sin localidad",
       "cat": "Catamarca", "sgo": "Santiago del Estero", "sju": "Salta y Jujuy",
       "otr": "Córdoba y otras provincias", "sa": "Sin asignar"}

# Sobre el texto sin tildes y en minúsculas. Una obra puede tener varias.
REGLAS_TECNICA = {
    "randa": r"\brand",
    "encaje": r"encaj|bolillo|puntilla",
    "filet": r"filet",
    "crochet": r"crochet|croche|irlanda|ganchillo",
    "deshilado": r"deshil",
    "bordado": r"bordad|richelieu",
    "telar": r"telar",
    "pala": r"\ba pala\b|baston",
}

# Instituciones: por el comienzo del nombre. "Mamerta Monteros -Escuela Sarmiento" es
# una persona de una escuela, no la escuela.
INSTITUCION = r"^(asilo|escuela|hermanas|colegio|superiora|sociedad|patronato|taller|instituto)\b"

# Sección del fallo de 1915 -> tipo de obra, para los premios sin objeto en el catálogo
FAM_SECCION = {"frazada": "tej", "poncho": "tej", "sendero": "tej", "alforja": "tej",
               "jergon": "tej", "alfombra": "alf", "randa": "enc", "panuelo": "enc",
               "encaje": "enc", "crochet": "enc", "deshilado": "bor", "bordado": "bor",
               "mantel": "bor", "raffia": "otr"}


def clave(s) -> str:
    return re.sub(r"\s+", " ", unidecode(str(s or "")).lower()).strip()


def slug(s) -> str:
    return re.sub(r"[^a-z0-9]+", "", clave(s))


def texto(v) -> str:
    return "" if pd.isna(v) else str(v).strip()


def frase(s: str) -> str:
    """'COLCHAS Y FRAZADAS' -> 'Colchas y frazadas'."""
    s = s.strip().lower()
    return s[:1].upper() + s[1:]


def tecnicas(txt: str, de_categoria: str) -> tuple[list[str], str]:
    t = clave(txt)
    hallo = [k for k, rx in REGLAS_TECNICA.items() if re.search(rx, t)]
    if hallo:
        return hallo, "o"
    if de_categoria:
        return [de_categoria], "c"
    return ["sin"], "n"


def leer_csv(ruta) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False)


# ------------------------------------------------------------------------- lugares
def lugares(C: pd.DataFrame, zona: dict[int, str]) -> tuple[dict, dict[int, str], int]:
    """Devuelve `places` (clave -> lugar), ciudad_id -> clave, y la clave de la sede."""
    C = C.copy()
    C["localidad"] = C["nombre_ciudad_hoy"].fillna(C["nombre_ciudad"])
    places, de_ciudad = {}, {}

    con_punto = C[C["lat"].notna()].copy()
    con_punto["pt"] = list(zip(con_punto["lat"].round(3), con_punto["lon"].round(3)))
    for pt, g in con_punto.groupby("pt", sort=False):
        g = g.sort_values("n_obj", ascending=False)
        top = g.iloc[0]
        k = slug(top["localidad"]) or f"c{top.ciudad_id}"
        while k in places:
            k += "_"
        notas = [n for n in g["nota"].map(nota_publica) if n]
        places[k] = {"n": texto(top["localidad"]), "p": texto(top["nombre_provincia"]),
                     "lat": round(float(top["lat"]), 4), "lon": round(float(top["lon"]), 4),
                     "t": "loc", "c": "aprox" if (g["precision"] == "tentativa").any() else "ok",
                     "note": " ".join(dict.fromkeys(notas))}
        for cid in g["ciudad_id"]:
            de_ciudad[int(cid)] = k

    a_prov = C[C["lat"].isna() & C["lat_provincia"].notna() & C["nombre_provincia"].notna()]
    for prov, g in a_prov.groupby("nombre_provincia", sort=False):
        k = "p_" + slug(prov)
        en_cat = sorted({texto(n) for n in g["nombre_ciudad"] if texto(n) and clave(n) != clave(prov)})
        nota = "Se conoce la provincia, no la localidad; el punto es la capital provincial."
        if en_cat:
            nota += " Localidades del catálogo todavía sin ubicar: " + ", ".join(en_cat) + "."
        places[k] = {"n": f"{prov} (solo provincia)", "p": prov,
                     "lat": round(float(g["lat_provincia"].iloc[0]), 4),
                     "lon": round(float(g["lon_provincia"].iloc[0]), 4),
                     "t": "prov", "c": "ok", "note": nota}
        for cid in g["ciudad_id"]:
            de_ciudad[int(cid)] = k

    for r in C[~C["ciudad_id"].isin(list(de_ciudad))].itertuples():
        k = f"c{r.ciudad_id}"
        n = texto(r.localidad) or "Sin dato"
        if clave(n) in ("s/d", "sd"):
            n = "Sin dato"
        nota = nota_publica(r.nota) or ("El catálogo no indica procedencia." if n == "Sin dato"
                                        else "Pendiente de georreferenciar.")
        places[k] = {"n": n, "p": texto(r.nombre_provincia) if texto(r.nombre_provincia) != "S/d" else "",
                     "lat": None, "lon": None, "t": "loc", "c": None, "note": nota}
        de_ciudad[int(r.ciudad_id)] = k

    for cid in C["ciudad_id"]:
        if int(cid) not in zona:
            print(f"  ⚠ ciudad_id {cid} sin fila en {ZONAS.name}: zona 'Sin asignar'")
    return places, de_ciudad, de_ciudad[SEDE_CIUDAD]


def nota_publica(v) -> str:
    """Saca de la nota la marca interna de revisión y lo que sólo es bitácora."""
    n = re.sub(r"^LM [\d-]+:\s*", "", texto(v))
    if re.match(r"(?i)coordenadas? (cargada|corregida)|coordenadas de san miguel", n):
        return ""
    return n[:1].upper() + n[1:] if n else ""


# ------------------------------------------------------------------------- premios
def premios(P: pd.DataFrame) -> list[dict]:
    """Una entrada por premio de la hoja Premios curada (etapa 04e).

    Cada premio lleva su `premio_id` (`pz.k`): un premio que abarca varias obras
    (Rosa Alderete, randas n.º 17 a 21) se cuelga de cada una, pero cuenta una vez.
    """
    out = []
    for _, r in P.iterrows():
        nombre = texto(r["Nombre en el fallo"])
        seccion, obj = texto(r["Sección del fallo"]), texto(r["Objeto en el fallo"])
        sec = clave(seccion)
        pr = clave(r["Premio"])
        if sec == "accesit":
            tipo = "Accésit"
        elif sec == "estimulo":
            tipo = "Premio de estímulo"
        elif pr.startswith("primer premio"):
            tipo = "Primer premio"
        elif pr.startswith("segundo premio"):
            tipo = "Segundo premio"
        else:
            tipo = "Premio"
        m = re.search(r"\d+", pr)
        ids = [int(float(x)) for x in re.split(r"[;,]", texto(r["objeto_id"])) if x.strip()]
        vinculo = clave(r["Vínculo"])
        if not ids:
            lk = "sv"
        elif texto(r["Estado"]) == "pendiente":
            lk = "nom?"
        elif vinculo.startswith("n.o"):
            lk = "ord"
        elif vinculo.startswith("decision a mano"):
            lk = "man"
        else:
            lk = "nom"
        obs = texto(r["Observaciones"])
        pid = r["persona_id"]
        out.append({
            "fila": int(r["premio_id"]), "nombre": nombre,
            "persona_id": None if pd.isna(pid) else int(pid),
            "ciudad": texto(r["Ciudad en el fallo"]), "provincia": texto(r["Provincia en el fallo"]),
            "objeto": obj, "num": texto(r["N.º"]), "seccion": seccion, "objetos": ids,
            "pz": {"k": int(r["premio_id"]), "t": tipo, "m": int(m.group()) if m else None,
                   "c": frase(seccion) if seccion else "Sin sección",
                   "ob": obs, "lk": lk, "foto": "foto" in clave(obs)},
        })
    return out


# ------------------------------------------------------------------------- armado
def datos() -> dict:
    xl = pd.ExcelFile(FUENTE)
    O = xl.parse("Objetos")
    E = xl.parse("Expositoras")
    K = xl.parse(next(s for s in xl.sheet_names if s.startswith("Categor")))
    C = xl.parse(next(s for s in xl.sheet_names if s.startswith("Ciudad")))
    crudos = pd.read_csv(CRUDOS, dtype={"objeto_id": int}).set_index("objeto_id")["nombre_raw"]
    F = leer_csv(FAMILIAS).assign(categoria_id=lambda d: d.categoria_id.astype(int)).set_index("categoria_id")
    Z = leer_csv(ZONAS)
    zona = {int(c): z for c, z in zip(Z.ciudad_id, Z.zona) if z in ZON}
    anio = dict(zip(xl.parse("Concursos").concurso_id, xl.parse("Concursos").anio))

    C["n_obj"] = C["ciudad_id"].map(O["ciudad_id"].value_counts()).fillna(0)
    places, de_ciudad, sede = lugares(C, zona)
    ciudad = C.set_index("ciudad_id")
    nombre = E.set_index("persona_id")["Nombre"]
    categoria = K.set_index("categoria_id")["nombre_categoria"]
    falta = set(O["categoria_id"]) - set(F.index)
    if falta:
        print(f"  ⚠ categorías sin fila en {FAMILIAS.name}: {sorted(falta)}")

    recs = []
    for o in O.sort_values("objeto_id").itertuples():
        n = texto(nombre.get(o.expositora_id)) or "Sin nombre"
        crudo = texto(crudos.get(o.objeto_id))
        nv = crudo.title() if crudo.isupper() else crudo
        fam = F.loc[o.categoria_id] if o.categoria_id in F.index else None
        cat = texto(categoria.get(o.categoria_id))
        tec, ts = tecnicas(texto(o.OBJETO), fam["tecnica_por_categoria"] if fam is not None else "")
        cr = ciudad.loc[o.ciudad_id]
        po = texto(cr["nombre_ciudad"]) or texto(cr["nombre_provincia"]) or "s/d"
        r = {"i": len(recs), "oid": int(o.objeto_id), "y": int(anio[o.concurso_id]),
             "n": n, "nv": nv if clave(nv) != clave(n) else n, "pk": str(o.expositora_id),
             "pl": de_ciudad[int(o.ciudad_id)], "po": "s/d" if clave(po) == "s/d" else po,
             "c": frase(cat), "f": fam["familia"] if fam is not None else "otr",
             "o": texto(o.OBJETO), "ord": str(o.ORDEN), "z": zona.get(int(o.ciudad_id), "sa"),
             "tec": tec, "ts": ts}
        if re.search(INSTITUCION, clave(n)):
            r["inst"] = 1
        recs.append(r)
    por_obj = {r["oid"]: r for r in recs}

    # premios: sobre la obra si hay vínculo; si no, como obra aparte
    lista = premios(xl.parse("Premios"))
    sin_obra = 0
    for z in lista:
        if z["objetos"]:
            for oid in z["objetos"]:
                if oid in por_obj:
                    por_obj[oid].setdefault("pz", []).append(z["pz"])
                else:
                    print(f"  ⚠ premio fila {z['fila']}: objeto_id {oid} no está en Objetos")
            continue
        sin_obra += 1
        recs.append(obra_sin_catalogo(z, recs, nombre, places, de_ciudad, C, zona))

    # la ficha que se abre al entrar: la expositora con más premios
    cuenta = Counter()
    for r in recs:
        cuenta[r["pk"]] += 10 * len(r.get("pz", [])) + 1
    stats = {"premios": len(lista), "sin_obra": sin_obra,
             "dudosos": sum(z["pz"]["lk"] == "nom?" for z in lista)}
    return {"places": places, "fam": FAM, "tec": TEC, "zon": ZON, "recs": recs,
            "sede": sede, "person0": cuenta.most_common(1)[0][0], "stats": stats}


def obra_sin_catalogo(z, recs, nombre, places, de_ciudad, C, zona) -> dict:
    """Premio del fallo sin objeto en el listado: una obra más, marcada `sv`."""
    pid = z["persona_id"]
    propias = [r for r in recs if pid is not None and r["pk"] == str(pid) and "sv" not in r]
    if propias:
        base = Counter((r["pl"], r["po"], r["z"]) for r in propias if r["y"] == 1915) \
            or Counter((r["pl"], r["po"], r["z"]) for r in propias)
        pl, po, zn = base.most_common(1)[0][0]
    else:
        pl, po, zn = lugar_del_fallo(z, places, de_ciudad, C, zona)
    n = texto(nombre.get(pid)) if pid is not None else z["nombre"]
    tec, ts = tecnicas(z["objeto"] + " " + z["seccion"], "")
    sec = clave(z["seccion"])
    fam = next((v for k, v in FAM_SECCION.items() if sec.startswith(k)), "otr")
    return {"i": len(recs), "y": 1915, "n": n, "nv": z["nombre"],
            "pk": str(pid) if pid is not None else "x:" + slug(z["nombre"]),
            "pl": pl, "po": po, "c": z["pz"]["c"], "f": fam, "o": z["objeto"],
            "ord": z["num"], "z": zn, "tec": tec, "ts": ts, "pz": [z["pz"]], "sv": 1,
            **({"inst": 1} if re.search(INSTITUCION, clave(n)) else {})}


def lugar_del_fallo(z, places, de_ciudad, C, zona) -> tuple[str, str, str]:
    """Lugar de un premio sin persona en la tabla, según la columna CIUDAD del fallo."""
    ciudad = z["ciudad"]
    if clave(ciudad) in ("", "s/d"):
        sd = C.loc[C["nombre_ciudad"].map(clave) == "s/d", "ciudad_id"]
        return de_ciudad[int(sd.iloc[0])], "s/d", "sa"
    cid = SEDE_CIUDAD if clave(ciudad) == "ciudad" else next(
        (int(c) for c, n in zip(C["ciudad_id"], C["nombre_ciudad"]) if clave(n) == clave(ciudad)), None)
    if cid is not None:
        return de_ciudad[cid], texto(C.set_index("ciudad_id").at[cid, "nombre_ciudad"]), zona.get(cid, "sa")
    k = "f_" + slug(ciudad)
    places.setdefault(k, {"n": ciudad.title(), "p": z["provincia"].title(), "lat": None, "lon": None,
                          "t": "loc", "c": None,
                          "note": "Figura sólo en el fallo del jurado; pendiente de georreferenciar."})
    return k, ciudad.title(), "tsl" if clave(z["provincia"]) == "tucuman" else "sa"


def js(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main() -> None:
    D = datos()
    plantilla = (PLANTILLAS / "explorador.template.html").read_text(encoding="utf-8")
    piezas = {
        "__LEAFLET_CSS__": (PLANTILLAS / "leaflet-1.9.4.css").read_text(encoding="utf-8").strip(),
        "__DATA__": js(D),
    }
    for k in piezas:
        assert plantilla.count(k) == 1, f"la plantilla tiene que tener {k} una sola vez"
    html = re.sub("|".join(piezas), lambda m: piezas[m.group()], plantilla)
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(html, encoding="utf-8", newline="\n")

    R, P = D["recs"], D["places"]
    print(f"{len(R)} obras ({sum('sv' in r for r in R)} premios sin obra en el catálogo) · "
          f"{sum('pz' in r for r in R)} obras premiadas · {len({r['pk'] for r in R})} expositoras")
    print(f"{len(P)} lugares: {sum(p['t'] == 'loc' and p['lat'] is not None for p in P.values())} con punto, "
          f"{sum(p['t'] == 'prov' for p in P.values())} sólo provincia, "
          f"{sum(p['lat'] is None for p in P.values())} sin ubicar "
          f"({sum(P[r['pl']]['lat'] is None for r in R)} obras)")
    print("técnica:", dict(Counter(r["ts"] for r in R)), "· zonas:", dict(Counter(r["z"] for r in R)))
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
