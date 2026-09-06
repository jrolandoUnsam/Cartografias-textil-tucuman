"""Corre el pipeline completo: 01 -> 06.

Uso:  python run_pipeline.py [desde]     (ej. `python run_pipeline.py 04`)
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ETAPAS = [
    "01_ingesta",
    "02_entidades",
    "03_candidatos",
    "04_normalizar",
    "05_vista_plana",
    "06_verificar",
]

PIPE = Path(__file__).resolve().parent / "src" / "pipeline"


def main() -> None:
    sys.path.insert(0, str(PIPE))
    desde = sys.argv[1] if len(sys.argv) > 1 else "01"
    for etapa in ETAPAS:
        if etapa[:2] < desde:
            continue
        print(f"\n=== {etapa} ===")
        runpy.run_path(str(PIPE / f"{etapa}.py"), run_name="__main__")


if __name__ == "__main__":
    main()
