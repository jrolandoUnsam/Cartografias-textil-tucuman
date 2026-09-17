"""Rutas y helpers compartidos por las etapas del pipeline."""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RAW_XLSX = RAIZ / "data" / "raw" / "TUCUMÁN text 1915-16 DATOS.xlsx"
INTERIM = RAIZ / "data" / "interim"
DECISIONES = INTERIM / "decisiones"
PROCESSED = RAIZ / "data" / "processed"
GOLDEN = RAIZ / "tests" / "golden"

def separar_orden_objeto(orden_celda: str, objeto_celda: str) -> list[tuple[int | None, str]]:
    """Separa filas 'explotadas' del catálogo de 1916.

    Una celda de orden como ``"2, 3, 4"`` con objeto
    ``"2, Frazada...; 3, Frazada...; 4, Frazada..."`` (o con los ítems separados
    por comas: ``"4 poncho..., 5 poncho..."``) devuelve una tupla ``(orden, objeto)``
    por cada ítem. Si no hay explosión devuelve un solo par.
    """
    orden_celda = (orden_celda or "").strip()
    objeto_celda = (objeto_celda or "").strip()

    ordenes = [int(x) for x in re.findall(r"\d+", orden_celda)]
    if len(ordenes) <= 1:
        n = ordenes[0] if ordenes else None
        if n is not None:
            objeto_celda = re.sub(rf"^\s*{n}\s*[,.\)]?\s+", "", objeto_celda)
        return [(n, objeto_celda)]

    def marca(n: int, desde: int) -> re.Match | None:
        return re.compile(rf"(?<!\d)({n})\s*[,.\)]?\s+").search(objeto_celda, desde)

    salida: list[tuple[int | None, str]] = []
    pos = 0
    for i, n in enumerate(ordenes):
        m = marca(n, pos)
        if i == 0:
            ini = m.end() if (m and m.start() <= 12) else 0
        else:
            ini = m.end() if m else pos
        sig = marca(ordenes[i + 1], ini) if i + 1 < len(ordenes) else None
        fin = sig.start() if sig else len(objeto_celda)
        texto = objeto_celda[ini:fin].strip().strip(";,").strip()
        salida.append((n, texto))
        pos = fin
    return salida
