# Cartografías del textil argentino (1915–1916)

Base de datos abierta y reproducible sobre el **1er Concurso Provincial de Tejidos y
Bordados** (Tucumán, 1915) y el **Concurso Interprovincial de Tejidos y Bordados**
(Tucumán, 1916): expositoras, objetos textiles, técnicas, localidades de procedencia
y premios.

Optativa interdisciplinaria LCD – CIAI – STD – UNSAM (2026).
Dirección: Larisa Mantovani (Escuela de Arte y Patrimonio / CIAP, CONICET‑UNSAM).

## Estado

En construcción. El corpus fue relevado y organizado por la investigadora en un Excel;
este repositorio reconstruye —en código, de forma reproducible— el camino desde ese
Excel crudo hasta las tablas normalizadas y la vista consolidada.

## Estructura

```
data/
  raw/          Excel original (nunca se edita) + imágenes de archivo (fuera del repo)
  interim/      resultados intermedios del pipeline y tablas de decisión manuales
  processed/    tabla_normalizada.xlsx, vista_plana_tabla_consolidada.xlsx
src/pipeline/   etapas del pipeline (01_ingesta … 06_verificar)
notebooks/      exploración y análisis
outputs/        figuras, mapas, tableros
docs/           bitácora de decisiones, diccionario de datos, evaluación de riesgos
tests/golden/   copias congeladas de las salidas, para verificación
```

## Cómo correrlo

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
python run_pipeline.py                               # corre 01 → 06
```

Cada etapa se puede correr suelta: `python src/pipeline/01_ingesta.py`.

## Flujo de datos

| Etapa | Entrada | Salida |
|---|---|---|
| `01_ingesta` | `data/raw/TUCUMÁN text 1915-16 DATOS.xlsx` | `data/interim/objetos_crudos.csv` |
| `02_entidades` | objetos_crudos | tablas provisionales de personas y ciudades |
| `03_candidatos` | tablas provisionales | `data/interim/revision_duplicados.xlsx` (se anota a mano) |
| `04_normalizar` | objetos_crudos + `revision_duplicados` anotado + `data/interim/decisiones/` | `data/processed/tabla_normalizada.xlsx` |
| `05_vista_plana` | tabla_normalizada | `data/processed/vista_plana_tabla_consolidada.xlsx` |
| `06_verificar` | salidas + `tests/golden/` | reporte de diferencias |

Los datos crudos no se modifican: toda transformación queda registrada en código.
Ver `docs/bitacora.md` para el registro de decisiones y `docs/diccionario_datos.md`
para la descripción de cada campo.

## Datos personales y ética

El corpus proviene de fuentes históricas públicas (catálogos y fallos de jurado de
1915–1916). Incluye nombres de personas —en su mayoría mujeres artesanas— fallecidas
hace más de un siglo; no hay datos personales sensibles en el sentido de la Ley 25.326.
Ver `docs/evaluacion_riesgos.md`.
