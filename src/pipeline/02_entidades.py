"""Etapa 02 — Entidades provisionales.  [EN CONSTRUCCIÓN]

De `data/interim/objetos_crudos.csv` extrae los listados provisionales de personas
y ciudades, asignando un id por orden de primera aparición (1915 antes que 1916).
Estos ids son el espacio de `id_A` / `id_B` de la etapa 03.

Salida:
  data/interim/personas_prov.csv   (persona_id, nombre_raw, Género inferido)
  data/interim/ciudades_prov.csv   (ciudad_id, nombre_raw)
"""
from __future__ import annotations

import pandas as pd

from _util import INTERIM


def main() -> None:
    c = pd.read_csv(INTERIM / "objetos_crudos.csv", dtype=str)

    personas = (
        c[["nombre_raw"]].drop_duplicates().reset_index(drop=True)
        .assign(persona_id=lambda d: d.index + 1)[["persona_id", "nombre_raw"]]
    )
    ciudades = (
        c[["ciudad_raw"]].drop_duplicates().reset_index(drop=True)
        .assign(ciudad_id=lambda d: d.index + 1)[["ciudad_id", "ciudad_raw"]]
    )
    personas.to_csv(INTERIM / "personas_prov.csv", index=False)
    ciudades.to_csv(INTERIM / "ciudades_prov.csv", index=False)
    print(f"{len(personas)} personas, {len(ciudades)} ciudades (provisionales)")
    # TODO: inferir Género del nombre de pila; marcar instituciones.
    # TODO: verificar que el espacio de ids coincide con id_A/id_B del golden.


if __name__ == "__main__":
    main()
