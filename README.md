# Cartografías del textil argentino (1915–1916)

Base de datos abierta y reproducible sobre el **1er Concurso Provincial de Tejidos y
Bordados** (Tucumán, 1915) y el **Concurso Interprovincial de Tejidos y Bordados**
(Tucumán, 1916): expositoras, objetos textiles, técnicas, localidades de procedencia
y premios.

Optativa interdisciplinaria LCD – CIAI – STD – UNSAM (2026).

- **Dirección:** Larisa Mantovani (Escuela de Arte y Patrimonio / CIAP, CONICET‑UNSAM).
- **Estudiante (LCD):** Julián Dante Rolando.
- **Tutoría:** Agustín Moro.

## Estado

En construcción. El corpus fue relevado y organizado por la investigadora en un Excel;
este repositorio reconstruye —en código, de forma reproducible— el camino desde ese
Excel crudo hasta las tablas normalizadas y la vista consolidada.

## Estructura

```
data/
  raw/          Excel original (nunca se edita) + imágenes de archivo (fuera del repo)
  interim/      resultados intermedios del pipeline y tablas de decisión manuales
    decisiones/ lo que no se deriva del crudo: fusiones, coordenadas, overrides
  processed/    tabla_normalizada.xlsx, vista_plana_tabla_consolidada.xlsx
src/pipeline/   etapas del pipeline (01_ingesta … 06b_controles)
notebooks/      exploración y análisis
outputs/        mapa_procedencias.html, explorador.html y controles_calidad.md
docs/           bitácora de decisiones, diccionario de datos, evaluación de riesgos
tests/golden/   copias congeladas de las salidas, para verificación
```

## Cómo correrlo

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows / PowerShell
pip install -r requirements.txt
python run_pipeline.py              # corre el pipeline completo
```

Con conda, en lugar de las dos primeras líneas:
`conda env create -f environment.yml && conda activate cartografias-textil`.

Desde una etapa en adelante: `python run_pipeline.py 04`. Una etapa suelta:
`python src/pipeline/01_ingesta.py`.

## Flujo de datos

Qué hace cada etapa, con qué entra y qué produce: **[`src/pipeline/README.md`](src/pipeline/README.md)**.

Los datos crudos no se modifican: toda transformación queda registrada en código. Las
decisiones que no se derivan del crudo (fusiones de expositoras, correcciones de texto,
cruces de premios) viven como tablas en `data/interim/decisiones/`, no dentro de los
scripts.

- [`docs/bitacora.md`](docs/bitacora.md) — registro cronológico de decisiones.
- [`docs/diccionario_datos.md`](docs/diccionario_datos.md) — descripción de cada campo.
- [`docs/tareas_pendientes.md`](docs/tareas_pendientes.md) — qué falta.
- [`docs/evaluacion_riesgos.md`](docs/evaluacion_riesgos.md) — sesgo y privacidad.
- [`docs/auditoria_comentarios.md`](docs/auditoria_comentarios.md) — informe generado:
  decisión anotada a mano vs. estado real de la tabla. Lo escribe
  `src/pipeline/audit_comentarios.py`, fuera de la corrida; no se edita a mano.
- [`outputs/controles_calidad.md`](outputs/controles_calidad.md) — informe generado en
  cada corrida (`06b_controles`): errores típicos de los catálogos para revisar.
- [`docs/referencias/README.md`](docs/referencias/README.md) — los PDF del marco
  institucional y del proyecto, que quedan fuera del repositorio.

## Datos personales y ética

El corpus proviene de fuentes históricas públicas (catálogos y fallos de jurado de
1915–1916). Incluye nombres de personas —en su mayoría mujeres artesanas— fallecidas
hace más de un siglo; no hay datos personales sensibles en el sentido de la Ley 25.326.
Ver [`docs/evaluacion_riesgos.md`](docs/evaluacion_riesgos.md).
