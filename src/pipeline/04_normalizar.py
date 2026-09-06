"""Etapa 04 — Normalización.  [EN CONSTRUCCIÓN]

Ensambla `data/processed/tabla_normalizada.xlsx` (6 hojas) a partir de:
  - data/interim/objetos_crudos.csv
  - data/interim/personas_prov.csv / ciudades_prov.csv
  - data/interim/revision_duplicados.xlsx  (anotado: se aplican los Hecho=True)
  - data/interim/decisiones/ciudades.csv    (nombre_ciudad_hoy, nombre_provincia)
  - data/interim/decisiones/categorias.csv  (unificaciones 1915/1916)
  - data/interim/decisiones/premios.csv     (hoja Premios, casi textual del fallo)

Hojas de salida: Concursos, Expositoras, Categorías, Ciudades, Objetos, Premios.
"""
from __future__ import annotations

# TODO: implementar.
#  - aplicar fusiones Hecho=True de revision_duplicados (regla: se conserva id_B,
#    salvo que el comentario indique otra cosa).
#  - resolver expositora_id / ciudad_id / categoria_id de cada objeto.
#  - Género, nombre_ciudad_hoy, nombre_provincia desde las tablas de decisión.
#  - respetar el orden de filas y el formato del golden
#    (tests/golden/tabla_normalizada.xlsx).

if __name__ == "__main__":
    raise SystemExit("04_normalizar: pendiente de implementar")
