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

Terminado (noviembre de 2026). El corpus fue relevado y organizado por la investigadora
en un Excel; este repositorio reconstruye en código, de forma reproducible, el camino
desde ese Excel hasta la base normalizada, la vista consolidada y el explorador web.

La base reúne 2 concursos, 458 expositoras (440 mujeres, 9 varones y 9 instituciones),
981 objetos, 102 premios y 77 localidades. Las preguntas que quedan abiertas sobre los
datos están en [`docs/tareas_pendientes.md`](docs/tareas_pendientes.md).

## Explorador

[`outputs/explorador.html`](outputs/explorador.html) es el producto principal: un único
archivo que se abre en el navegador, sin servidor ni conexión. Tiene seis pestañas:
Presentación, Mapa, Análisis, Expositoras, Galería y Red. Cada ficha de obra indica su
fuente (catálogo, página y escaneo) y trae su cita lista para copiar.

## Estructura

```
data/
  raw/          Excel original (nunca se edita) + imágenes de archivo (fuera del repo)
  interim/      resultados intermedios del pipeline y tabla manual de partida
    decisiones/ 16 tablas con lo que no se deriva del crudo: fusiones, nombres,
                coordenadas, premios, técnicas, prensa, etc.
  processed/    tabla_normalizada.xlsx, vista_plana_tabla_consolidada.xlsx, redes.xlsx
src/pipeline/   15 etapas (01_ingesta … 15_controles) y audit_comentarios.py
notebooks/      eda.ipynb (análisis exploratorio) y revision_duplicados.ipynb
outputs/        explorador.html, mapa_procedencias.html, controles_calidad.md y redes.md
docs/           bitácora, diccionario de datos, evaluación de riesgos y pendientes
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

Desde una etapa en adelante: `python run_pipeline.py 06`. Una etapa suelta:
`python src/pipeline/01_ingesta.py`.

Los escaneos de los catálogos y del álbum no están en el repositorio (ver
`data/raw/images/README.md`). Sin ellos el pipeline corre igual: el explorador usa las
versiones livianas de las fotos que sí están versionadas.

## Flujo de datos

Qué hace cada etapa, con qué entra y qué produce: **[`src/pipeline/README.md`](src/pipeline/README.md)**.

Los datos crudos no se modifican: toda transformación queda registrada en código. Las
decisiones que no se derivan del crudo (fusiones de expositoras, correcciones de texto,
cruces de premios, técnicas) viven como tablas en `data/interim/decisiones/`, no dentro
de los scripts.

- [`docs/bitacora.md`](docs/bitacora.md): registro cronológico de decisiones.
- [`docs/diccionario_datos.md`](docs/diccionario_datos.md): descripción de cada campo.
- [`docs/tareas_pendientes.md`](docs/tareas_pendientes.md): preguntas abiertas y mejoras posibles.
- [`docs/evaluacion_riesgos.md`](docs/evaluacion_riesgos.md): sesgo y privacidad.
- [`docs/relevamiento_prensa_archivo.md`](docs/relevamiento_prensa_archivo.md): repaso de
  las hojas de prensa y archivo del Excel crudo: qué se aprovechó y dónde quedó.
- [`docs/auditoria_comentarios.md`](docs/auditoria_comentarios.md): informe generado:
  decisión anotada a mano vs. estado real de la tabla. Lo escribe
  `src/pipeline/audit_comentarios.py`, fuera de la corrida; no se edita a mano.
- [`outputs/controles_calidad.md`](outputs/controles_calidad.md): informe generado en
  cada corrida (`15_controles`): errores típicos de los catálogos para revisar.
- [`outputs/redes.md`](outputs/redes.md): informe generado en cada corrida
  (`12_redes`): redes de participación; el grafo está en `data/processed/redes.xlsx`.
- [`docs/referencias/README.md`](docs/referencias/README.md): los PDF del marco
  institucional y del proyecto, que quedan fuera del repositorio.

## Cómo citar

Mantovani, Larisa; Rolando, Julián y Moro, Agustín. (2026). *Cartografías del textil
argentino: Producción y exhibición a partir de datos históricos e imágenes de archivo*
[Conjunto de datos de investigación]. CIAP-CONICET / UNSAM.

## Datos personales y ética

El corpus proviene de fuentes históricas públicas (catálogos y fallos de jurado de
1915–1916). Incluye nombres de personas (en su mayoría mujeres artesanas) fallecidas
hace más de un siglo; no hay datos personales sensibles en el sentido de la Ley 25.326.
Ver [`docs/evaluacion_riesgos.md`](docs/evaluacion_riesgos.md).
