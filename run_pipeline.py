"""Corre el pipeline completo: 01 -> 06.

Uso:  python run_pipeline.py [desde]     (ej. `python run_pipeline.py 04` o `04d`)

El detalle de qué hace cada etapa está en `src/pipeline/README.md`.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ETAPAS = [
    "01_ingesta",
    "03_candidatos",
    "04_aplicar_dedup",
    "04b_titulo_nombres",
    "04c_vincular_imagenes",
    "04d_coordenadas",
    "04e_premios",
    "04f_marcas_objetos",
    "05_vista_plana",
    "05b_mapa",
    "05c_explorador",
    "06_verificar",
]

PIPE = Path(__file__).resolve().parent / "src" / "pipeline"


def main() -> None:
    sys.path.insert(0, str(PIPE))
    desde = sys.argv[1] if len(sys.argv) > 1 else "01"
    for etapa in ETAPAS:
        # se compara con tantos caracteres como tenga `desde`: "04" corre 04, 04b, …;
        # "04d" arranca en 04d
        if etapa[:len(desde)] < desde:
            continue
        print(f"\n=== {etapa} ===")
        runpy.run_path(str(PIPE / f"{etapa}.py"), run_name="__main__")


if __name__ == "__main__":
    main()
