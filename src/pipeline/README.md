# Pipeline

Reconstruye, en código, el camino desde el Excel crudo hasta las tablas normalizadas.

| etapa | estado | qué hace |
|---|---|---|
| `01_ingesta` | **funciona** | raw xlsx → `data/interim/objetos_crudos.csv` (981 objetos; separa filas explotadas de 1916) |
| `02_entidades` | esqueleto | listados provisionales de personas y ciudades (id por aparición) |
| `03_candidatos` | **funciona** | fuzzy matching → `data/interim/revision_duplicados.xlsx` (salida que se anota a mano; no pisa anotaciones previas). Ver `notebooks/03_revision_duplicados.ipynb` para revisar |
| `03b_premios` | **funciona** | agrega a una copia de la hoja `Premios` las columnas `persona_id` / `objeto_id` (misma cantidad de filas, mismo orden) → `data/interim/premios_vinculados.xlsx`. Correcciones a mano en `data/interim/decisiones/premios_manual.csv` |
| `04_normalizar` | pendiente | ensambla `tabla_normalizada.xlsx` (6 hojas) |
| `05_vista_plana` | **funciona** | join de `tabla_normalizada.xlsx` → `data/processed/vista_plana_tabla_consolidada.xlsx` (981 filas; orden: concurso, categoría, expositora, y dentro del grupo el orden del catálogo) |
| `06_verificar` | **funciona** | compara `data/processed/` y `revision_duplicados` contra `tests/golden/` |
| `audit_comentarios` | **funciona** | audita fila por fila si cada comentario de `revision_duplicados` y de la hoja `Premios` se aplicó a `tabla_normalizada.xlsx` → `docs/auditoria_comentarios.md` |

Correr todo: `python run_pipeline.py` (desde la raíz). Una etapa suelta:
`python src/pipeline/01_ingesta.py`.

## Insumos que no salen del crudo (tablas de decisión, en `data/interim/decisiones/`)

- `objetos_texto_override.csv` — celdas de texto que la investigadora corrigió a mano
  respecto del catálogo (erratas, singular/plural, mayúsculas). Ya poblada con las
  detectadas al comparar contra el golden.
- `ciudades.csv` *(pendiente)* — `nombre_ciudad_hoy` y `nombre_provincia` de cada
  localidad histórica.
- `categorias.csv` *(pendiente)* — unificaciones de categorías entre 1915 y 1916.
- `premios.csv` *(pendiente)* — hoja Premios (casi textual del fallo del jurado).

## Nota sobre el "golden"

`tests/golden/` son copias congeladas del estado actual de las salidas. Es un
snapshot a mitad de normalización (dedup parcial) y tiene algún dato a revisar
—p. ej. los objetos de la sección TAPICES de 1916 figuran con la categoría RANDAS—.
Ver `docs/bitacora.md`.
