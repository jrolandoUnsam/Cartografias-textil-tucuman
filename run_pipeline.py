"""Corre el pipeline completo: 01 -> 14.

Uso:  python run_pipeline.py [desde]     (ej. `python run_pipeline.py 06`)

El detalle de qué hace cada etapa está en `src/pipeline/README.md`.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ETAPAS = [
    "01_ingesta",
    "02_candidatos",
    "03_fusiones",
    "04_nombres",
    "05_imagenes",
    "06_coordenadas",
    "07_premios",
    "08_marcas",
    "09_tecnicas",
    "10_vista_plana",
    "11_redes",
    "12_mapa",
    "13_explorador",
    "14_controles",
]

PIPE = Path(__file__).resolve().parent / "src" / "pipeline"


def main() -> None:
    sys.path.insert(0, str(PIPE))
    desde = sys.argv[1] if len(sys.argv) > 1 else "01"
    codigo = 0
    for etapa in ETAPAS:
        # se compara con tantos caracteres como tenga `desde`: "06" arranca en 06_coordenadas
        if etapa[:len(desde)] < desde:
            continue
        print(f"\n=== {etapa} ===")
        # si una etapa termina con sys.exit(), la corrida sigue con las demás y el
        # código se devuelve al final
        try:
            runpy.run_path(str(PIPE / f"{etapa}.py"), run_name="__main__")
        except SystemExit as e:
            if e.code:
                codigo = e.code
    sys.exit(codigo)


if __name__ == "__main__":
    main()
