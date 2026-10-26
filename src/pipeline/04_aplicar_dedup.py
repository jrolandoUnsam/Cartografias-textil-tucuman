"""Etapa 04 — Aplicar las fusiones de expositoras duplicadas.

PASO 3 del flujo de deduplicación:

    03_candidatos.py    detecta pares candidatos
    (a mano)            se anota Hecho / Comentarios en duplicados_expositoras_candidatos.xlsx
    04_aplicar_dedup.py ejecuta las decisiones anotadas          (este script)

Cada decisión es una fila de `data/interim/decisiones/fusiones_expositoras.csv`:
para cada id de `descartar`, mueve sus objetos (`Objetos.expositora_id`) al id
`mantener` y borra esa fila de `Expositoras`. Queda una sola persona por decisión,
con todos sus objetos juntos. Los premios de la hoja `Premios` que apuntaban a un id
descartado pasan a apuntar al id que queda (`persona_id` y `persona`).

La columna `origen` dice de dónde sale la decisión:

  decidida  el comentario de la revisión dice explícitamente qué lado se conserva.
  sin_lado  el comentario dice "unificar" sin aclarar qué id queda. Como el nombre
            ya quedó idéntico en los dos lados, el número no cambia el resultado
            visible; sí cambia cuántos objetos hay que mover. Criterio aplicado:
            conservar el lado con más objetos (menos movimientos).
  cluster   grupo de 3+ ids resuelto como una sola decisión, no par por par.

Después de fusionar, `data/interim/decisiones/nombres_expositoras.csv` (persona_id,
nombre, nota, genero) fija el nombre con que queda una expositora, p. ej. la variante entre
corchetes que acordamos con Larisa al unificar ("Facunda Cerone [Coronel]"), y, si
`genero` no está vacío, corrige el `Género` de la tabla manual (F / M). Un `nombre`
vacío deja el nombre como está. Se aplica antes de reapuntar los premios, así la hoja
Premios ya muestra el nombre final.

Lo mismo que las expositoras, para ciudades, con
`data/interim/decisiones/fusiones_ciudades.csv` (mismo formato): el mismo lugar cargado
con dos ids ("SANTIAGO" / "SANTIAGO DEL ESTERO"). Los objetos pasan a
`Objetos.ciudad_id = mantener` y la fila descartada sale de `Ciudades`. Cómo lo
escribió el catálogo no se pierde: la vista plana lo muestra en "Lugar en el
documento", tomado del crudo.

Y al revés, `data/interim/decisiones/separaciones_ciudades.csv` (ciudad_id_nueva,
ciudad_id_origen, objetos, nombre_ciudad, nota): un `ciudad_id` que junta envíos de
lugares distintos ("CHACO": la Misión de Nueva Pompeya y Amelia Zunubate) se parte en
dos. Se crea la fila `ciudad_id_nueva` en `Ciudades` (provincia copiada del origen) y
los objetos listados pasan a ella. Su ubicación va en `coordenadas_ciudades.csv`, como
la de cualquier otra ciudad.

Antes de todo, cada celda de texto de todas las hojas pasa por `limpiar_texto`
(`_util.py`): sin espacios al principio ni al final y con uno solo entre palabras. La
tabla manual no se toca; la limpieza vale desde esta etapa en adelante.

Entrada : data/interim/tabla_normalizada_manual.xlsx   (export manual más reciente,
          con las revisiones de Larisa en la hoja Premios)
          data/interim/decisiones/fusiones_expositoras.csv
          data/interim/decisiones/nombres_expositoras.csv
          data/interim/decisiones/fusiones_ciudades.csv
          data/interim/decisiones/separaciones_ciudades.csv
Salida  : data/interim/tabla_normalizada_dedup.xlsx   (insumo de 04b)
"""
from __future__ import annotations

import csv
from dataclasses import dataclass

import pandas as pd

from _util import DECISIONES, INTERIM, limpiar_texto

FUENTE = INTERIM / "tabla_normalizada_manual.xlsx"
SALIDA = INTERIM / "tabla_normalizada_dedup.xlsx"
FUSIONES_CSV = DECISIONES / "fusiones_expositoras.csv"
NOMBRES_CSV = DECISIONES / "nombres_expositoras.csv"
FUSIONES_CIUDADES_CSV = DECISIONES / "fusiones_ciudades.csv"
SEPARACIONES_CSV = DECISIONES / "separaciones_ciudades.csv"


@dataclass
class Fusion:
    mantener: int
    descartar: list[int]
    origen: str = ""
    nota: str = ""


def leer_fusiones(ruta=FUSIONES_CSV) -> list[Fusion]:
    with ruta.open(encoding="utf-8", newline="") as fh:
        return [
            Fusion(
                mantener=int(r["mantener"]),
                descartar=[int(x) for x in r["descartar"].split()],
                origen=r.get("origen", ""),
                nota=r.get("nota", ""),
            )
            for r in csv.DictReader(fh)
        ]


def aplicar(E: pd.DataFrame, O: pd.DataFrame, fusiones: list[Fusion]):
    E, O = E.copy(), O.copy()
    log = []
    for f in fusiones:
        movidos = []
        for d in f.descartar:
            n = int((O["expositora_id"] == d).sum())
            O.loc[O["expositora_id"] == d, "expositora_id"] = f.mantener
            movidos.append((d, n))
        E = E[~E["persona_id"].isin(f.descartar)]
        log.append((f.mantener, movidos, f.nota))
    return E, O, log


def renombrar(E: pd.DataFrame, ruta=NOMBRES_CSV) -> pd.DataFrame:
    E = E.copy()
    for _, r in pd.read_csv(ruta).iterrows():
        pid = int(r["persona_id"])
        fila = E["persona_id"] == pid
        if not fila.any():
            raise ValueError(f"{ruta.name}: persona_id {pid} no existe después de las fusiones")
        if pd.notna(r["nombre"]):
            print(f"  {pid}: {E.loc[fila, 'Nombre'].iloc[0]!r} -> {r['nombre']!r}")
            E.loc[fila, "Nombre"] = r["nombre"]
        if pd.notna(r.get("genero")):
            print(f"  {pid}: género {E.loc[fila, 'Género'].iloc[0]} -> {r['genero']}")
            E.loc[fila, "Género"] = r["genero"]
    return E


def fusionar_ciudades(C: pd.DataFrame, O: pd.DataFrame, fusiones: list[Fusion]):
    ids = set(C["ciudad_id"])
    C, O = C.copy(), O.copy()
    for f in fusiones:
        faltan = [i for i in [f.mantener] + f.descartar if i not in ids]
        if faltan:
            raise ValueError(f"{FUSIONES_CIUDADES_CSV.name}: ciudad_id {faltan} no existe "
                             f"en {FUENTE.name} ({f.nota})")
        n = int(O["ciudad_id"].isin(f.descartar).sum())
        O.loc[O["ciudad_id"].isin(f.descartar), "ciudad_id"] = f.mantener
        C = C[~C["ciudad_id"].isin(f.descartar)]
        print(f"  -> queda ciudad {f.mantener} ({n} obj. de {f.descartar}): {f.nota}")
    assert set(O["ciudad_id"].dropna()) <= set(C["ciudad_id"]), "quedaron objetos sin ciudad"
    return C, O


def separar_ciudades(C: pd.DataFrame, O: pd.DataFrame, ruta=SEPARACIONES_CSV):
    C, O = C.copy(), O.copy()
    for _, r in pd.read_csv(ruta).iterrows():
        nueva, origen = int(r["ciudad_id_nueva"]), int(r["ciudad_id_origen"])
        objetos = [int(x) for x in str(r["objetos"]).split()]
        if nueva in set(C["ciudad_id"]):
            raise ValueError(f"{ruta.name}: el ciudad_id {nueva} ya existe")
        if origen not in set(C["ciudad_id"]):
            raise ValueError(f"{ruta.name}: el ciudad_id {origen} no existe")
        de_otro = O.loc[O["objeto_id"].isin(objetos) & (O["ciudad_id"] != origen), "objeto_id"]
        faltan = set(objetos) - set(O["objeto_id"])
        if faltan or len(de_otro):
            raise ValueError(f"{ruta.name}: objetos {sorted(faltan) + list(de_otro)} no son "
                             f"de la ciudad {origen}")
        fila = C[C["ciudad_id"] == origen].copy()
        fila["ciudad_id"], fila["nombre_ciudad"] = nueva, r["nombre_ciudad"]
        if "nombre_ciudad_hoy" in fila.columns:
            fila["nombre_ciudad_hoy"] = None
        C = pd.concat([C, fila], ignore_index=True)
        O.loc[O["objeto_id"].isin(objetos), "ciudad_id"] = nueva
        print(f"  -> ciudad {origen} se separa: {len(objetos)} obj. pasan a {nueva} "
              f"({r['nombre_ciudad']}): {r['nota']}")
    return C, O


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}
    for s, df in hojas.items():
        cambios = 0
        for c in df.columns:
            if df[c].dtype == object or pd.api.types.is_string_dtype(df[c]):
                limpio = df[c].map(limpiar_texto)
                cambios += int((df[c].notna() & (limpio != df[c])).sum())
                df[c] = limpio
        if cambios:
            print(f"  {s}: {cambios} celdas con espacios de más")
    E, O = hojas["Expositoras"], hojas["Objetos"]
    ids = set(E["persona_id"])

    validas = []
    for f in leer_fusiones():
        if f.mantener not in ids:
            print(f"AVISO — se omite entera (el id a conservar {f.mantener} ya no "
                  f"existe en {FUENTE.name}): {f.nota}")
            continue
        for d in f.descartar:
            if d not in ids:
                print(f"AVISO — {f.nota}: el id {d} ya no existe en "
                      f"{FUENTE.name}, se ignora")
        vivos = [d for d in f.descartar if d in ids]
        if vivos:
            validas.append(Fusion(f.mantener, vivos, f.origen, f.nota))

    E2, O2, log = aplicar(E, O, validas)
    print(f"\nnombres fijados ({NOMBRES_CSV.name}):")
    E2 = renombrar(E2)

    # La hoja Premios también apunta a expositoras: si no se reapunta, un premio
    # queda colgado de un id que la fusión acaba de borrar.
    if "Premios" in hojas and "persona_id" in hojas["Premios"].columns:
        P = hojas["Premios"].copy()
        destino = {d: f.mantener for f in validas for d in f.descartar}
        nombre = E2.set_index("persona_id")["Nombre"]
        afectadas = P["persona_id"].isin(list(destino))
        for idx in P.index[afectadas]:
            viejo = int(P.at[idx, "persona_id"])
            P.at[idx, "persona_id"] = destino[viejo]
            if "persona" in P.columns:
                P.at[idx, "persona"] = nombre[destino[viejo]]
            print(f"  Premios fila {idx}: persona_id {viejo} -> {destino[viejo]}")
        hojas["Premios"] = P

    print(f"\n{len(log)} fusiones aplicadas · "
          f"{len(E) - len(E2)} filas de Expositoras eliminadas")
    for mantener, movidos, nota in log:
        detalle = ", ".join(f"{n} obj. de {d}" for d, n in movidos)
        print(f"  -> queda {mantener}: {nota}  [{detalle}]")

    # sanity check: ids duplicados / objetos huérfanos
    assert E2["persona_id"].is_unique, "quedaron ids de expositora duplicados"
    assert set(O2["expositora_id"]) <= set(E2["persona_id"]), "quedaron objetos huérfanos"

    fus_c = leer_fusiones(FUSIONES_CIUDADES_CSV)
    print(f"\n{len(fus_c)} fusiones de ciudades")
    hojas["Ciudades"], O2 = fusionar_ciudades(hojas["Ciudades"], O2, fus_c)
    print("\nseparaciones de ciudades")
    hojas["Ciudades"], O2 = separar_ciudades(hojas["Ciudades"], O2)

    hojas["Expositoras"], hojas["Objetos"] = E2, O2
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)
    print(f"\n-> {SALIDA}")


if __name__ == "__main__":
    main()
