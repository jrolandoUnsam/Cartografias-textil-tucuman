"""Etapa 05c — Explorador web (mapa, técnicas por provincia, expositoras).

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

  familias_categorias.csv   por categoría, `tecnica_por_categoria`: la técnica que se
                            asume cuando el texto del objeto no menciona ninguna, y
                            `material_por_categoria`: el que nombra la sección del
                            catálogo (Chales de vicuña, Raffia imitación con hojas de caña)
  tecnicas_materiales.csv   términos de técnica y material validados por LM (28/10/2026):
                            etiqueta, técnica general (`grupo`) y regla sobre el texto

Las zonas (`zonas_ciudades.csv`) y los tipos de obra (columna `familia` de
`familias_categorias.csv`) eran agrupaciones propuestas por el proyecto sin respaldo en
las fuentes; desde el 28/10 el explorador no las usa hasta que LM las revise. La
procedencia se agrupa por provincia, la misma que muestra el mapa.

Las técnicas y los materiales se leen del texto del objeto con las reglas de
`tecnicas_materiales.csv` (`_tecnicas.py`, las mismas que dejan las columnas de `04h` en
la base); el texto del catálogo no se toca. Si no hay técnica, se usa la de la categoría
(`ts = "c"`); si tampoco, queda "sin técnica indicada" (`ts = "n"`).

El género de cada obra (`g`: F, M o I) es el de su expositora en la hoja `Expositoras`.

Lugares: un círculo por localidad actual (`nombre_ciudad_hoy` + provincia), como en
`05b_mapa`: "La Cocha" y "Escuela de la Cocha", o "Asilo Ciudad" y San Miguel, van
juntos; el punto es el de la fila con más obras. Lo que no tiene punto
de ciudad pero sí provincia se agrupa en un lugar "sólo provincia" en la capital, como
en `05b_mapa`. Lo que no tiene ninguno de los dos queda sin coordenadas: se lista en
la matriz y en las fichas, no en el mapa.

Los grupos de expositoras con el mismo apellido en el mismo lugar salen de la hoja
`Grupos` de `redes.xlsx` (`05a_redes`, que corre antes): se muestran en Análisis y en
cada ficha como pista de parentesco, no como dato.
La pestaña Red dibuja el grafo completo (hojas Nodos y Aristas) con sigma.js y graphology,
que la página carga de un CDN con versión fija, como Leaflet.

Entrada : data/processed/tabla_normalizada.xlsx (Objetos, Expositoras, Categorías,
          Ciudades, Premios), data/interim/objetos_crudos.csv (nombre tal como figura
          en el catálogo), data/processed/redes.xlsx (Grupos, Nodos y Aristas), decisiones/*.csv
Salida  : outputs/explorador.html
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date

import pandas as pd

from _tecnicas import FAMILIAS, GRUPO, MAT, TEC, clave, familias, leer_csv, materiales, tecnicas
from _util import DECISIONES, INSTITUCION, INTERIM, PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
CRUDOS = INTERIM / "objetos_crudos.csv"
PRENSA = DECISIONES / "menciones_prensa.csv"
COMISIONES = DECISIONES / "comisiones.csv"
REDES = PROCESSED / "redes.xlsx"  # hoja Grupos, de 05a_redes
PLANTILLAS = RAIZ / "src" / "pipeline" / "plantillas"
SALIDA = RAIZ / "outputs" / "explorador.html"

SEDE_CIUDAD = 2  # San Miguel de Tucumán: sede de los dos concursos


def slug(s) -> str:
    return re.sub(r"[^a-z0-9]+", "", clave(s))


def texto(v) -> str:
    return "" if pd.isna(v) else str(v).strip()


def frase(s: str) -> str:
    """'COLCHAS Y FRAZADAS' -> 'Colchas y frazadas'."""
    s = s.strip().lower()
    return s[:1].upper() + s[1:]


# ------------------------------------------------------------------------- lugares
def lugares(C: pd.DataFrame) -> tuple[dict, dict[int, str], int]:
    """Devuelve `places` (clave -> lugar), ciudad_id -> clave, y la clave de la sede."""
    C = C.copy()
    C["localidad"] = C["nombre_ciudad_hoy"].fillna(C["nombre_ciudad"])
    places, de_ciudad = {}, {}

    con_punto = C[C["lat"].notna()]
    for _, g in con_punto.groupby(["localidad", "nombre_provincia"], sort=False, dropna=False):
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
        pendiente = texto(r["Estado"]) == "pendiente"
        if not ids:
            lk = "pen" if pendiente else "sv"  # pendiente de vincular / fuera de catálogo
        elif pendiente:
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
    F = familias()
    anio = dict(zip(xl.parse("Concursos").concurso_id, xl.parse("Concursos").anio))
    pagina = paginas(O, xl.parse("Paginas_Catalogo"), K)

    C["n_obj"] = C["ciudad_id"].map(O["ciudad_id"].value_counts()).fillna(0)
    places, de_ciudad, sede = lugares(C)
    ciudad = C.set_index("ciudad_id")
    nombre = E.set_index("persona_id")["Nombre"]
    genero = E.set_index("persona_id")["Género"]
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
        mat = materiales(texto(o.OBJETO), fam["material_por_categoria"] if fam is not None else "")
        # procedencia como la escribió el catálogo, aunque 04d haya pasado la obra a la
        # localidad de la expositora
        cat_id = getattr(o, "ciudad_id_catalogo", None)
        cr = ciudad.loc[int(cat_id) if pd.notna(cat_id) else o.ciudad_id]
        po = texto(cr["nombre_ciudad"]) or texto(cr["nombre_provincia"]) or "s/d"
        r = {"i": len(recs), "oid": int(o.objeto_id), "y": int(anio[o.concurso_id]),
             "n": n, "nv": nv if clave(nv) != clave(n) else n, "pk": str(o.expositora_id),
             "pl": de_ciudad[int(o.ciudad_id)], "po": "s/d" if clave(po) == "s/d" else po,
             "c": frase(cat), "o": texto(o.OBJETO), "ord": str(o.ORDEN),
             "tec": tec, "ts": ts, "cit": cita(int(anio[o.concurso_id]), pagina.get(o.objeto_id), o.imagen)}
        if mat:
            r["mat"] = mat
        if texto(genero.get(o.expositora_id)):
            r["g"] = texto(genero.get(o.expositora_id))  # F, M o I (institución)
        if re.search(INSTITUCION, clave(n)):
            r["inst"] = 1
        # marcas que pone 04f leyendo el texto del catálogo
        if texto(getattr(o, "fuera_de_concurso", "")) == "sí":
            r["fc"] = 1
        if texto(getattr(o, "creacion_autora", "")) == "sí":
            r["ca"] = 1
        if pd.notna(cat_id):
            r["li"] = 1  # localidad deducida de las otras obras de la expositora (04d)
        if texto(getattr(o, "foto_album", "")):
            r["fa"] = texto(o.foto_album)  # foto del álbum de 1915 (04c)
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
                    print(f"  ⚠ premio_id {z['fila']}: objeto_id {oid} no está en Objetos")
            continue
        sin_obra += 1
        recs.append(obra_sin_catalogo(z, recs, nombre, genero, places, de_ciudad, C))

    # provincia de cada obra: la del lugar en que la muestra el mapa
    n_prov = Counter(places[r["pl"]]["p"] for r in recs)
    prv = {slug(p) or "sd": p or "Sin dato" for p, _ in sorted(n_prov.items(), key=lambda x: (not x[0], -x[1]))}
    for r in recs:
        r["pv"] = slug(places[r["pl"]]["p"]) or "sd"

    # prensa de época: la mención va a la obra, a la ficha de la persona o al lugar
    fuentes = xl.parse("Fuentes")
    diario = {int(f): texto(d).split(",")[0] for f, d in zip(fuentes.fuente_id, fuentes.descripcion)}
    prensa = []
    for m in leer_csv(PRENSA).itertuples():
        oids = [int(x) for x in m.objeto_id.split(";") if x.strip()]
        lugares_m = [de_ciudad[int(c)] for c in m.ciudad_id.split(";") if c.strip() and int(c) in de_ciudad]
        k = len(prensa)
        for oid in oids:
            if oid in por_obj:
                por_obj[oid].setdefault("pr", []).append(k)
            else:
                print(f"  ⚠ {PRENSA.name}: objeto_id {oid} no está en Objetos")
        if m.persona_id and int(m.persona_id) not in set(O["expositora_id"]):
            print(f"  ⚠ {PRENSA.name}: persona_id {m.persona_id} no está en Expositoras")
        y, mes, d = m.fecha.split("-")
        prensa.append({"d": diario.get(int(m.fuente_id), ""), "f": f"{int(d)}/{int(mes)}/{y}", "t": m.titulo,
                       "c": m.cita, "pk": m.persona_id, "pl": lugares_m})

    # comisión organizadora y jurado; si comparte apellido con expositoras, se dice cuáles
    # (solo eso: el apellido no prueba parentesco)
    comision = []
    for c in leer_csv(COMISIONES).itertuples():
        apellido = clave(c.nombre).split()[-1]
        mismo = [] if c.persona_id else sorted(
            {texto(n) for pid, n in nombre.items() if apellido in clave(n).replace("[", " ").replace("]", " ").split()})
        comision.append({"a": int(c.anio), "n": c.nombre, "nf": c.nombre_en_fuente, "r": c.rol, "s": c.seccion,
                         "f": c.fuente, "pk": c.persona_id, "mismo": mismo})

    # grupos con el mismo apellido en el mismo lugar (05a_redes): una pista de parentesco
    redes = [{"ap": g.apellidos, "l": g.lugar, "c": g.confianza, "pk": str(g.persona_ids).split(";")}
             for g in pd.read_excel(REDES, sheet_name="Grupos").itertuples()] if REDES.exists() else []
    # la red completa, para la pestaña Red: nodos [id, tipo, nombre, persona_id, concursos,
    # provincia, obras, premios] y aristas [origen, destino, tipo, detalle, confianza, peso]
    red = {"n": [], "e": []}
    if REDES.exists():
        N = pd.read_excel(REDES, sheet_name="Nodos")
        A = pd.read_excel(REDES, sheet_name="Aristas")
        num = lambda v: int(v) if pd.notna(v) else 0  # noqa: E731
        red["n"] = [[n.id, n.tipo, texto(n.nombre), str(num(n.persona_id)) if pd.notna(n.persona_id) else "",
                     texto(n.concursos), texto(n.provincia), num(n.obras) or num(n.expositoras), num(n.premios)]
                    for n in N.itertuples()]
        red["e"] = [[a.origen, a.destino, a.tipo, texto(a.detalle), a.confianza, num(a.peso)] for a in A.itertuples()]

    # la ficha que se abre al entrar: la expositora con más premios
    cuenta = Counter()
    for r in recs:
        cuenta[r["pk"]] += 10 * len(r.get("pz", [])) + 1
    lks = Counter(z["pz"]["lk"] for z in lista)
    stats = {"premios": len(lista), "sin_obra": sin_obra, "fuera": lks["sv"],
             "pendientes": lks["pen"], "dudosos": lks["nom?"]}
    return {"places": places, "tec": TEC, "tecg": GRUPO, "mat": MAT, "prv": prv, "recs": recs,
            "sede": sede, "person0": cuenta.most_common(1)[0][0], "stats": stats,
            "version": fecha_larga(date.today()), "prensa": prensa, "comision": comision, "redes": redes, "red": red,
            "fuentes": [{k: texto(v) for k, v in f.items()} for f in fuentes.to_dict("records")],
            "concursos": [{k: texto(v) for k, v in c.items()} for c in xl.parse("Concursos").to_dict("records")]}


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def paginas(O: pd.DataFrame, Pg: pd.DataFrame, K: pd.DataFrame) -> dict:
    """objeto_id -> página impresa del catálogo, por escaneo, sección y rango de N.º
    (`Paginas_Catalogo`). Un escaneo puede tener dos páginas y varias secciones."""
    cat = K.set_index("categoria_id")["nombre_categoria"].map(clave)
    Pg = Pg.dropna(subset=["orden_desde", "orden_hasta", "pagina_impresa"])
    out = {}
    for o in O.itertuples():
        c = Pg[(Pg["imagen"] == o.imagen) & Pg["orden_desde"].le(o.ORDEN) & Pg["orden_hasta"].ge(o.ORDEN)
               & (Pg["categoria_o_seccion"].map(clave).str[:6] == cat[o.categoria_id][:6])]
        if len(c) == 1:
            out[o.objeto_id] = int(c["pagina_impresa"].iloc[0])
    return out


def cita(anio: int, pagina, imagen) -> str:
    """'Catálogo de 1916, p. 13 (DSCN5201)': de dónde sale la obra, para ir a la fuente."""
    esc = re.sub(r"\.jpe?g$", "", texto(imagen), flags=re.I)
    return f"Catálogo de {anio}" + (f", p. {pagina}" if pagina else "") + (f" ({esc})" if esc else "")


def obra_sin_catalogo(z, recs, nombre, genero, places, de_ciudad, C) -> dict:
    """Premio del fallo sin objeto en el listado: una obra más, marcada `sv`."""
    pid = z["persona_id"]
    propias = [r for r in recs if pid is not None and r["pk"] == str(pid) and "sv" not in r]
    if propias:
        base = Counter((r["pl"], r["po"]) for r in propias if r["y"] == 1915) \
            or Counter((r["pl"], r["po"]) for r in propias)
        pl, po = base.most_common(1)[0][0]
    else:
        pl, po = lugar_del_fallo(z, places, de_ciudad, C)
    n = texto(nombre.get(pid)) if pid is not None else z["nombre"]
    tec, ts = tecnicas(z["objeto"] + " " + z["seccion"], "")
    # el material sólo del objeto: la sección "Bordado en blanco y seda" no dice que la obra sea de seda
    mat = materiales(z["objeto"], "")
    g = texto(genero.get(pid)) if pid is not None else ""
    return {"i": len(recs), "y": 1915, "n": n, "nv": z["nombre"],
            **({"mat": mat} if mat else {}), **({"g": g} if g else {}),
            "pk": str(pid) if pid is not None else "x:" + slug(z["nombre"]),
            "pl": pl, "po": po, "c": z["pz"]["c"], "o": z["objeto"],
            "ord": z["num"], "tec": tec, "ts": ts, "pz": [z["pz"]], "sv": 1,
            "cit": "Fallo del jurado de 1915" + (f", {frase(z['seccion'])}" if z["seccion"] else ""),
            **({"inst": 1} if re.search(INSTITUCION, clave(n)) else {})}


def lugar_del_fallo(z, places, de_ciudad, C) -> tuple[str, str]:
    """Lugar de un premio sin persona en la tabla, según la columna CIUDAD del fallo."""
    ciudad = z["ciudad"]
    if clave(ciudad) in ("", "s/d"):
        sd = C.loc[C["nombre_ciudad"].map(clave) == "s/d", "ciudad_id"]
        return de_ciudad[int(sd.iloc[0])], "s/d"
    cid = SEDE_CIUDAD if clave(ciudad) == "ciudad" else next(
        (int(c) for c, n in zip(C["ciudad_id"], C["nombre_ciudad"]) if clave(n) == clave(ciudad)), None)
    if cid is not None:
        return de_ciudad[cid], texto(C.set_index("ciudad_id").at[cid, "nombre_ciudad"])
    k = "f_" + slug(ciudad)
    places.setdefault(k, {"n": ciudad.title(), "p": z["provincia"].title(), "lat": None, "lon": None,
                          "t": "loc", "c": None,
                          "note": "Figura sólo en el fallo del jurado; pendiente de georreferenciar."})
    return k, ciudad.title()


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
    print("técnica:", dict(Counter(r["ts"] for r in R)), "· provincias:", dict(Counter(r["pv"] for r in R)))
    print("materiales:", dict(Counter(m for r in R for m in r.get("mat", []))))
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
