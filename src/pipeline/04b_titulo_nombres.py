"""Etapa 04b — Pasar a Título los nombres que están TODO EN MAYÚSCULA.

Ejemplo: "EDELMIRA C. DE ROLDÁN" -> "Edelmira C. de Roldán".

Reglas:
  - Solo toca celdas que están enteramente en mayúscula (si ya tienen mezcla de
    mayúsculas/minúsculas, como "S? de Plaza" o "María J. de Aguirre", no se tocan).
  - Cada palabra queda con la primera letra en mayúscula y el resto en minúscula
    ("ROLDÁN" -> "Roldán"), incluso si tiene apóstrofo o guión ("D'EMPAIRE" -> "D'Empaire").
  - Las partículas de/del/la/las/los/y quedan en minúscula salvo que sean la
    primera palabra del nombre.
  - Las iniciales con punto quedan igual ("C." -> "C.").
  - No agrega ni saca tildes: si la mayúscula no tenía tilde, el resultado tampoco.
  - Los espacios de más ya los sacó `04_aplicar_dedup` (`limpiar_texto`).

Entrada : data/interim/tabla_normalizada_dedup.xlsx   (salida de 04_aplicar_dedup)
Salida  : data/processed/tabla_normalizada.xlsx
"""
from __future__ import annotations

import re

import pandas as pd

from _util import INTERIM, PROCESSED

FUENTE = INTERIM / "tabla_normalizada_dedup.xlsx"
SALIDA = PROCESSED / "tabla_normalizada.xlsx"

HOJAS_Y_COLUMNAS = {
    "Expositoras": ["Nombre"],
    "Ciudades": ["nombre_ciudad", "nombre_ciudad_hoy", "nombre_provincia"],
}

PARTICULAS = {"de", "del", "la", "las", "los", "y"}


def es_todo_mayuscula(s: str) -> bool:
    s = str(s)
    return s.upper() == s and s.lower() != s  # tiene letras y ninguna es minúscula


def _capitaliza_palabra(palabra: str) -> str:
    """'ROLDÁN' -> 'Roldán'; "D'EMPAIRE" -> "D'Empaire"; 'C.' -> 'C.'"""
    chars = list(palabra.lower())
    mayuscula_siguiente = True
    for i, ch in enumerate(chars):
        if ch.isalpha():
            if mayuscula_siguiente:
                chars[i] = ch.upper()
            mayuscula_siguiente = False
        elif ch in ("'", "-"):
            mayuscula_siguiente = True
    return "".join(chars)


def a_titulo(nombre: str) -> str:
    if not es_todo_mayuscula(nombre):
        return nombre
    palabras = str(nombre).split(" ")
    out = []
    for i, p in enumerate(palabras):
        nucleo = re.sub(r"[^\wÁÉÍÓÚÑáéíóúñ]", "", p).lower()
        if nucleo in PARTICULAS and i != 0:
            out.append(p.lower())
        else:
            out.append(_capitaliza_palabra(p))
    return " ".join(out)


def main() -> None:
    xl = pd.ExcelFile(FUENTE)
    hojas = {s: xl.parse(s) for s in xl.sheet_names}

    total_cambios = 0
    for hoja, columnas in HOJAS_Y_COLUMNAS.items():
        if hoja not in hojas:
            continue
        df = hojas[hoja]
        for col in columnas:
            if col not in df.columns:
                continue
            nuevos = df[col].map(a_titulo)
            cambios = (nuevos.astype(str) != df[col].astype(str)) & df[col].notna()
            for idx in df.index[cambios]:
                print(f"  {hoja}.{col} fila {idx}: {df.at[idx, col]!r} -> {nuevos.at[idx]!r}")
            total_cambios += int(cambios.sum())
            df[col] = nuevos

    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        for s, df in hojas.items():
            df.to_excel(w, sheet_name=s, index=False)

    print(f"\n{total_cambios} celdas pasadas a título")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()
