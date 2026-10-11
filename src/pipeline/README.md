# Pipeline

Reconstruye, en código, el camino desde el Excel crudo hasta las tablas normalizadas.
**Esta es la descripción canónica del flujo**: el README de la raíz apunta acá en vez
de repetirla.

Correr todo: `python run_pipeline.py` (desde la raíz). Desde una etapa en adelante:
`python run_pipeline.py 04`. Una etapa suelta: `python src/pipeline/01_ingesta.py`.

| etapa | entrada | salida | estado |
|---|---|---|---|
| `01_ingesta` | `data/raw/TUCUMÁN text 1915-16 DATOS.xlsx` | `data/interim/objetos_crudos.csv` (981 objetos; separa las filas explotadas de 1916) | funciona |
| `02_entidades` | objetos_crudos | `personas_prov.csv`, `ciudades_prov.csv` (id por orden de aparición) | esqueleto; **su salida no la consume ninguna etapa** |
| `03_candidatos` | `data/interim/tabla_normalizada_manual.xlsx` (Expositoras, Ciudades, Objetos) | `data/interim/duplicados_expositoras_candidatos.xlsx` — 85 filas (75 detectadas hoy + 10 conservadas de corridas anteriores), con `Hecho`/`Comentarios` para anotar. Conserva las anotaciones y los pares que ya figuraban. Al final imprime cuántos quedan **sin fusionar y sin revisar**: hoy son 10 (otros 10, no los conservados — ver `docs/tareas_pendientes.md`) | funciona |
| `03b_premios` | `data/processed/tabla_normalizada.xlsx` (Premios) ⚠ ver abajo | `data/interim/premios_vinculados.xlsx` — misma cantidad de filas y mismo orden, con `persona_id`/`objeto_id` agregados. **Callejón sin salida: no lo lee ninguna etapa** | funciona |
| `04_aplicar_dedup` | `data/interim/tabla_normalizada_manual.xlsx` + `decisiones/fusiones_expositoras.csv` | `data/interim/tabla_normalizada_dedup.xlsx` — 42 decisiones en el CSV, **41 aplicadas**, 519 → 471 expositoras. Dos ids a descartar ya no existen en la tabla manual (67 y 117) y el script los avisa; la fila `76,67` queda sin efecto por eso | funciona |
| `04b_titulo_nombres` | tabla_normalizada_dedup | `data/processed/tabla_normalizada.xlsx` (nombres ALLCAPS → Título) | funciona |
| `04c_vincular_imagenes` | tabla_normalizada + hoja `Paginas_Catalogo` | tabla_normalizada con la columna `Objetos.imagen` — 981/981 objetos con imagen | funciona |
| `04d_coordenadas` | tabla_normalizada + `decisiones/coordenadas_ciudades.csv` | tabla_normalizada con las columnas `Ciudades.lat`/`Ciudades.lon` — 53/77 ciudades con coordenada | funciona |
| `05_vista_plana` | tabla_normalizada | `data/processed/vista_plana_tabla_consolidada.xlsx` (981 filas, incluye `lat`/`lon` e `Imagen`) | funciona |
| `06_verificar` | salidas + `tests/golden/` | reporte de diferencias, hoja por hoja | corre, pero **hoy falla siempre**: el golden está desactualizado (ver abajo) |
| `audit_comentarios` | tabla_normalizada + `tabla_normalizada_manual.xlsx` | `docs/auditoria_comentarios.md` | funciona, fuera de la corrida |

## Aciclicidad: qué se arregló y qué falta

`03_candidatos` leía `data/processed/tabla_normalizada.xlsx`, que es lo que escriben
`04b` y `04c` — dos etapas **posteriores**. Eso cerraba un ciclo: la etapa 03 leía la
salida de la corrida anterior, y el resultado encogía en cada pasada (519 expositoras →
75 pares; después de las fusiones, 471 → 22), reescribiendo el archivo anotable con
menos filas de las que tenía.

Hoy las tres etapas que necesitan una línea de base leen **la misma y fija**,
`data/interim/tabla_normalizada_manual.xlsx`: `03_candidatos`, `04_aplicar_dedup` y
`audit_comentarios`.

**Queda un ciclo sin cerrar: `03b_premios`.** Lee `data/processed/tabla_normalizada.xlsx`,
que escriben `04b`, `04c` y `04d` — tres etapas posteriores —, así que trabaja sobre la
tabla de la corrida anterior. No afecta al resto del pipeline, porque su salida
(`premios_vinculados.xlsx`) no la consume nadie, pero el cruce de nombres corre contra
nombres ya fusionados y ya pasados a título en vez de contra la línea de base. Está
anotado en `docs/tareas_pendientes.md`; el arreglo es apuntarlo a
`tabla_normalizada_manual.xlsx`, igual que `03_candidatos`.

Con esa excepción, ninguna etapa lee la salida de una posterior. Verificado el
2026-09-18: corriendo `python run_pipeline.py` sobre el repo limpio, las cinco salidas
quedan **idénticas celda por celda** a las commiteadas (cambia sólo la metadata del zip
de cada `.xlsx`, así que `git status` las marca como modificadas igual).

Además, `03_candidatos` nunca destruye trabajo manual: relee su propia salida y
conserva `Hecho`/`Comentarios` emparejados por `(id_A, id_B)`, y mantiene los pares ya
listados aunque la detección de hoy no los proponga (columna `detectado`). Es la regla
que `docs/bitacora.md` fijaba desde el principio y que el código no implementaba.

## Dónde empieza el código

`data/processed/tabla_normalizada.xlsx` **no se arma desde el crudo**. La investigadora
la mantiene a mano en Excel (`data/interim/tabla_normalizada_manual.xlsx`) y el pipeline
en código arranca ahí: `04_aplicar_dedup` → `04b_titulo_nombres` → `04c_vincular_imagenes`.

Automatizar también ese primer armado (crudo + tablas de decisión → tabla normalizada)
era la etapa `04_normalizar`, que no llegó a implementarse y se quitó del repo. Si
alguna vez se retoma, faltaría: resolver `expositora_id`/`ciudad_id`/`categoria_id` de
cada objeto, el `Género`, y `nombre_ciudad_hoy`/`nombre_provincia` desde las tablas de
decisión. Está en `git log` (commit `975476e`).

## Insumos que no salen del crudo (`data/interim/decisiones/`)

- `fusiones_expositoras.csv` — las 42 fusiones de expositoras duplicadas
  (`mantener`, `descartar`, `origen`, `nota`). Cada fila corresponde a una decisión
  anotada en `duplicados_expositoras_candidatos.xlsx`. `origen` dice si el comentario
  indicaba explícitamente qué lado conservar (`decidida`), si no lo indicaba y se
  aplicó el criterio "conservar el lado con más objetos" (`sin_lado`), o si es un
  grupo de 3+ ids resuelto en conjunto (`cluster`).
- `objetos_texto_override.csv` — celdas de texto que la investigadora corrigió a mano
  respecto del catálogo (erratas, singular/plural, mayúsculas).
- `premios_manual.csv` — correcciones al cruce Premios ↔ Objetos. Acepta
  `objeto_id = "ninguno"` para forzar que un premio quede sin objeto.
- `coordenadas_ciudades.csv` — `lat`/`lon` de cada ciudad (`ciudad_id`), cargadas a
  mano por la investigadora (Google Maps). 53/77 cargadas; el resto queda vacío
  (nombre ambiguo o desconocido) hasta que se complete o se decida un criterio.
- `ciudades.csv` *(pendiente)* — `nombre_ciudad_hoy` y `nombre_provincia`.
- `categorias.csv` *(pendiente)* — unificaciones de categorías entre 1915 y 1916.

## Parámetros

El único parámetro del pipeline es `UMBRAL = 87` en `03_candidatos.py`: el ratio
mínimo (0–100) de `rapidfuzz` para proponer un par de nombres como candidato a
duplicado. No hay modelos entrenados ni semillas de aleatoriedad.

## Sobre `tests/golden/`

Ver `tests/golden/README.md`. Resumen: es un snapshot congelado, no un test. Vale como
verificación **solo si no se re-congela en el mismo commit que cambia el pipeline**.

**Estado al 2026-09-18: desactualizado, y por eso `06_verificar` falla siempre.** El
golden nunca se re-congeló después de que `04d` agregara `lat`/`lon` a `Ciudades` y
`04c` agregara `Imagen` a la vista plana:

```
tabla_normalizada.xlsx        [Ciudades] shape (78, 6) != golden (78, 4)
vista_plana_consolidada.xlsx  [Objetos - Concursos Tucumán] shape (982, 10) != golden (982, 7)
```

Las demás hojas dan OK. Re-congelarlo en un commit propio es una tarea pendiente
(`docs/tareas_pendientes.md`).
