"""Etapa 12: Mapa de procedencias.

Genera `outputs/mapa_procedencias.html` (folium) a partir de la tabla normalizada, así
el mapa se regenera con cada corrida y no queda desfasado de los datos. Hasta
2026-10-13 lo hacía a mano `notebooks/eda.ipynb` y quedó con nombres y coordenadas
viejas ("Villa Vitulumba", Orán con punto).

Dos capas:

  Ciudades     un círculo por localidad actual (`nombre_ciudad_hoy` + provincia) con
               `lat`/`lon`: "Escuela de la Cocha" y "La Cocha", o las dos filas de
               Cafayate, van en un solo círculo aunque sus coordenadas difieran en unos
               metros; el punto es el de la fila con más objetos. Si la ubicación es
               `tentativa`, lo dice el popup.
  Provincias   lo que no tiene punto de ciudad pero sí provincia (sólo provincia, o
               ciudad sin ubicar) se suma en la capital de la provincia
               (`lat_provincia`/`lon_provincia`), con otro color y borde punteado,
               como en el explorador. Pedido de Larisa, 2026-10.

Folium pone ids al azar a cada elemento; se reemplazan por números correlativos para
que dos corridas den el mismo archivo.

Lo que no tiene ni ciudad ni provincia ubicadas no aparece; el total se informa en la
consola.

Entrada : data/processed/tabla_normalizada.xlsx (Objetos, Ciudades)
Salida  : outputs/mapa_procedencias.html
"""
from __future__ import annotations

import html
import re

import folium
import pandas as pd

from _util import PROCESSED, RAIZ

FUENTE = PROCESSED / "tabla_normalizada.xlsx"
SALIDA = RAIZ / "outputs" / "mapa_procedencias.html"

COLOR_CIUDAD = "#2f4b6e"
COLOR_PROVINCIA = "#c27c0e"
TILES = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/"
         "MapServer/tile/{z}/{y}/{x}")


def _radio(objetos: int) -> float:
    return 3 + objetos ** .5 * 1.6


def _cuantos(n: int, uno: str, varios: str) -> str:
    return f"{n} {uno if n == 1 else varios}"


def _lista(valores) -> str:
    return ", ".join(sorted({str(v) for v in valores if pd.notna(v)}))


def puntos(fuente=FUENTE) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    xl = pd.ExcelFile(fuente)
    O = xl.parse("Objetos")
    C = xl.parse(next(s for s in xl.sheet_names if s.startswith("Ciudad")))
    C["localidad"] = C["nombre_ciudad_hoy"].fillna(C["nombre_ciudad"])
    g = O.merge(C, on="ciudad_id", how="left")

    con_ciudad = g["lat"].notna()
    gc = g[con_ciudad].copy()
    # el punto de cada localidad: el de la fila de Ciudades con más objetos
    n = gc.groupby("ciudad_id").size()
    gc["_n"] = gc["ciudad_id"].map(n)
    punto = (gc.sort_values(["_n", "ciudad_id"], ascending=[False, True])
             .drop_duplicates(["localidad", "nombre_provincia"])
             .set_index(["localidad", "nombre_provincia"])[["lat", "lon"]])
    ciudades = (gc.groupby(["localidad", "nombre_provincia"], dropna=False)
                .agg(objetos=("objeto_id", "size"),
                     expositoras=("expositora_id", "nunique"),
                     en_catalogo=("nombre_ciudad", _lista),
                     tentativa=("precision", lambda s: (s == "tentativa").any()))
                .join(punto)
                .reset_index()
                .rename(columns={"nombre_provincia": "provincia"}))

    a_provincia = ~con_ciudad & g["lat_provincia"].notna()
    provincias = (g[a_provincia]
                  .groupby(["nombre_provincia", "lat_provincia", "lon_provincia"])
                  .agg(objetos=("objeto_id", "size"),
                       expositoras=("expositora_id", "nunique"),
                       en_catalogo=("nombre_ciudad", _lista))
                  .reset_index())

    sin_ubicar = int((~con_ciudad & ~a_provincia).sum())
    return ciudades, provincias, sin_ubicar


def mapa(ciudades: pd.DataFrame, provincias: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[-27.2, -65.3], zoom_start=6, tiles=None)
    folium.TileLayer(TILES, attr="Esri", name="Mapa base (Esri)").add_to(m)

    capa_c = folium.FeatureGroup(name="Ciudades", show=True)
    for _, r in ciudades.iterrows():
        nota = "<br><i>ubicación tentativa</i>" if r.tentativa else ""
        popup = (f"<b>{html.escape(r.localidad)}</b> ({html.escape(str(r.provincia))})<br>"
                 f"{_cuantos(r.objetos, 'objeto', 'objetos')} · "
                 f"{_cuantos(r.expositoras, 'expositora', 'expositoras')}<br>"
                 f"en el catálogo: {html.escape(r.en_catalogo)}{nota}")
        folium.CircleMarker(
            [r.lat, r.lon], radius=_radio(r.objetos), color=COLOR_CIUDAD,
            fill=True, fill_opacity=.5,
            popup=folium.Popup(popup, max_width=300), tooltip=r.localidad,
        ).add_to(capa_c)
    capa_c.add_to(m)

    capa_p = folium.FeatureGroup(name="Sólo provincia (en la capital)", show=True)
    for _, r in provincias.iterrows():
        cat = f"<br>en el catálogo: {html.escape(r.en_catalogo)}" if r.en_catalogo else ""
        popup = (f"<b>{html.escape(r.nombre_provincia)}</b>: sin ciudad ubicada<br>"
                 f"{_cuantos(r.objetos, 'objeto', 'objetos')} · "
                 f"{_cuantos(r.expositoras, 'expositora', 'expositoras')}{cat}<br>"
                 f"<i>punto de referencia: capital de la provincia</i>")
        folium.CircleMarker(
            [r.lat_provincia, r.lon_provincia], radius=_radio(r.objetos),
            color=COLOR_PROVINCIA, fill=True, fill_opacity=.4, dash_array="4",
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"{r.nombre_provincia} (sólo provincia)",
        ).add_to(capa_p)
    capa_p.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def main() -> None:
    ciudades, provincias, sin_ubicar = puntos()
    SALIDA.parent.mkdir(exist_ok=True)
    texto = mapa(ciudades, provincias).get_root().render()
    # folium bloquea el zoom con los dedos; se deja hacer, como en el explorador
    texto, n = re.subn(r"initial-scale=1\.0, maximum-scale=1\.0, user-scalable=no",
                       "initial-scale=1.0", texto)
    assert n == 1, "cambió el viewport de folium"
    ids: dict[str, str] = {}
    texto = re.sub(r"(?<=_)[0-9a-f]{32}(?![0-9a-f])",
                   lambda m: ids.setdefault(m.group(), f"{len(ids) + 1:04d}"), texto)
    SALIDA.write_text(texto, encoding="utf-8")
    print(f"{len(ciudades)} puntos de ciudad ({ciudades.objetos.sum()} objetos) · "
          f"{len(provincias)} puntos de provincia ({provincias.objetos.sum()} objetos) · "
          f"{sin_ubicar} objetos sin ubicar")
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
