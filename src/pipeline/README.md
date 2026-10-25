# Pipeline

Reconstruye, en código, el camino desde el Excel crudo hasta las tablas normalizadas.
**Esta es la descripción canónica del flujo**: el README de la raíz apunta acá en vez
de repetirla.

Correr todo: `python run_pipeline.py` (desde la raíz). Desde una etapa en adelante:
`python run_pipeline.py 04`. Una etapa suelta: `python src/pipeline/01_ingesta.py`.

| etapa | entrada | salida | estado |
|---|---|---|---|
| `01_ingesta` | `data/raw/TUCUMÁN text 1915-16 DATOS.xlsx` | `data/interim/objetos_crudos.csv` (981 objetos; separa las filas explotadas de 1916) | funciona |
| `03_candidatos` | `data/interim/tabla_normalizada_manual.xlsx` (Expositoras, Ciudades, Objetos) | `data/interim/duplicados_expositoras_candidatos.xlsx` — 85 filas (75 detectadas hoy + 10 conservadas de corridas anteriores), con `Hecho`/`Comentarios` para anotar. Conserva las anotaciones y los pares que ya figuraban. Al final imprime cuántos quedan **sin fusionar y sin revisar**: hoy son 10 (otros 10, no los conservados — ver `docs/tareas_pendientes.md`) | funciona |
| `04_aplicar_dedup` | `data/interim/tabla_normalizada_manual.xlsx` + `decisiones/fusiones_expositoras.csv`, `nombres_expositoras.csv`, `fusiones_ciudades.csv`, `separaciones_ciudades.csv` | `data/interim/tabla_normalizada_dedup.xlsx` — 55 decisiones en el CSV, **54 aplicadas**, 519 → 458 expositoras; 1 fusión de ciudades (50 → 5). Dos ids a descartar ya no existen en la tabla manual (67 y 117) y el script los avisa; la fila `76,67` queda sin efecto por eso | funciona |
| `04b_titulo_nombres` | tabla_normalizada_dedup | `data/processed/tabla_normalizada.xlsx` (nombres ALLCAPS → Título) | funciona |
| `04c_vincular_imagenes` | tabla_normalizada + hoja `Paginas_Catalogo` | tabla_normalizada con la columna `Objetos.imagen` — 981/981 objetos con imagen | funciona |
| `04d_coordenadas` | tabla_normalizada + `decisiones/coordenadas_ciudades.csv` | tabla_normalizada con la ubicación de cada ciudad tomada del CSV: `nombre_ciudad_hoy`, `nombre_provincia`, `lat`/`lon`, `lat_provincia`/`lon_provincia`, `precision`, `nota` — 58/77 ciudades con coordenada, 68/77 con punto de provincia | funciona |
| `04e_premios` | `tabla_normalizada_dedup.xlsx` (Premios de la tabla manual) + tabla_normalizada (Expositoras, Objetos) + `decisiones/premios_manual.csv` | tabla_normalizada con la hoja `Premios` curada: un premio por fila, con su obra del catálogo, `Estado` (vinculado / fuera de catálogo / pendiente), `Vínculo` y `Nota` — 102 premios: 89 vinculados, 11 fuera de catálogo, 2 pendientes | funciona |
| `04f_marcas_objetos` | tabla_normalizada (Objetos) | tabla_normalizada con `Objetos.fuera_de_concurso` (2) y `Objetos.creacion_autora` (12), leídas del texto del catálogo, que no se toca | funciona |
| `05_vista_plana` | tabla_normalizada | `data/processed/vista_plana_tabla_consolidada.xlsx` (981 filas, incluye `lat`/`lon` e `Imagen`) | funciona |
| `05b_mapa` | tabla_normalizada | `outputs/mapa_procedencias.html` (folium): capa de ciudades (57 puntos, 756 objetos; borde punteado si la ubicación es tentativa) y capa "sólo provincia" en la capital (8 puntos, 181 objetos); 44 objetos sin ubicar. Antes lo exportaba `notebooks/04_eda.ipynb`, que ahora sólo lo muestra | funciona |
| `05c_explorador` | tabla_normalizada (incluida la hoja Premios) + `objetos_crudos.csv` + `decisiones/familias_categorias.csv`, `decisiones/zonas_ciudades.csv` | `outputs/explorador.html`: explorador web autocontenido (mapa, técnicas por zona, fichas de expositoras) a partir de la plantilla `plantillas/explorador.template.html`. 994 obras = 981 objetos + 13 premios de 1915 sin obra en el catálogo. Técnicas inferidas por reglas sobre el texto del objeto (si no, la de la categoría) | funciona |
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

**El último ciclo, `03b_premios`, se cerró el 2026-10-25.** Leía
`data/processed/tabla_normalizada.xlsx` de la corrida anterior y dejaba su resultado en
`premios_vinculados.xlsx`, que nadie consumía. Ahora es `04e_premios`: corre después de
`04d` sobre la tabla de la misma corrida, toma los premios de la tabla manual (vía
`tabla_normalizada_dedup.xlsx`) y escribe la hoja `Premios` curada.

Ninguna etapa lee la salida de una posterior. Verificado el
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

- `fusiones_expositoras.csv` — las fusiones de expositoras duplicadas (55 filas)
  (`mantener`, `descartar`, `origen`, `nota`). Cada fila corresponde a una decisión
  anotada en `duplicados_expositoras_candidatos.xlsx`. `origen` dice si el comentario
  indicaba explícitamente qué lado conservar (`decidida`), si no lo indicaba y se
  aplicó el criterio "conservar el lado con más objetos" (`sin_lado`), o si es un
  grupo de 3+ ids resuelto en conjunto (`cluster`).
- `nombres_expositoras.csv` — nombre con que queda una expositora después de fusionar
  (`persona_id`, `nombre`, `nota`), p. ej. la variante entre corchetes acordada con
  Larisa ("Facunda Cerone [Coronel]"). Lo aplica `04_aplicar_dedup`.
- `fusiones_ciudades.csv` — mismo lugar cargado con dos `ciudad_id` (mismo formato que
  las fusiones de expositoras). Lo aplica `04_aplicar_dedup`; el texto del catálogo
  sigue visible en la vista plana ("Lugar en el documento").
- `separaciones_ciudades.csv` — al revés que una fusión: un `ciudad_id` que junta
  envíos de lugares distintos se parte; se crea `ciudad_id_nueva` y los `objetos`
  listados pasan a ella. Lo aplica `04_aplicar_dedup`. Hoy: "CHACO" (53) → Misión
  Franciscana de Nueva Pompeya (82).
- `album_1915.csv` — transcripción de LM de las fotos del álbum de 1915 (foto, n.º,
  descripción, posición en la foto). Todavía no la lee ninguna etapa.
- `objetos_texto_override.csv` — celdas de texto que la investigadora corrigió a mano
  respecto del catálogo (erratas, singular/plural, mayúsculas).
- `premios_manual.csv` — correcciones al cruce Premios ↔ Objetos. Acepta
  `objeto_id = "ninguno"` para forzar que un premio quede sin objeto.
- `coordenadas_ciudades.csv` — la única fuente de la ubicación de cada ciudad
  (`ciudad_id`): `nombre_ciudad_hoy`, `nombre_provincia`, `lat`/`lon` (cargadas a mano
  por la investigadora, Google Maps), `lat_provincia`/`lon_provincia` (capital),
  `precision` y `nota`. `04d` pisa con esto la copia de la tabla manual. 53/77 con
  punto de ciudad; el resto queda vacío (nombre ambiguo o desconocido).
- `familias_categorias.csv` — por categoría, el tipo de obra (`familia`) y la técnica que se
  asume cuando el texto del objeto no nombra ninguna (`tecnica_por_categoria`). Lo usa
  `05c_explorador`. Propuesta de esta versión, a validar con la dirección.
- `zonas_ciudades.csv` — zona de cada `ciudad_id` para el explorador. La propuesta inicial
  salió de la provincia y la distancia a la capital (columna `criterio`); se corrige a mano.
- `tecnicas_materiales.csv` — términos de técnica, proceso y material que aparecen en
  los textos de las obras (patrón, propuesta de nombre, cantidad de obras, ejemplo),
  para que los valide LM (`validacion_LM`). Todavía no la lee ninguna etapa; validada,
  reemplaza a `REGLAS_TECNICA` de `05c_explorador`.
- `categorias.csv` *(pendiente)* — unificaciones de categorías entre 1915 y 1916.

## Parámetros

Todos son umbrales de parecido de nombres (0–100, `rapidfuzz`). No hay modelos
entrenados ni semillas de aleatoriedad. Cada cambio queda en `docs/bitacora.md`.

| parámetro | dónde | valor | para qué |
|---|---|---|---|
| `UMBRAL` | `03_candidatos.py` | 80 | parecido mínimo del nombre entero para proponer un par como duplicado (era 87) |
| `UMBRAL_APELLIDO` | `03_candidatos.py` | 75 | en la regla de nombres "compatibles", parecido mínimo del apellido |
| `UMBRAL_NOMBRE` | `04e_premios.py` | 60 | el dueño del objeto tiene que parecerse al nombre del premio para aceptar el vínculo |
| `UMBRAL_ELEGIR` | `04e_premios.py` | 80 | con varios objetos con el mismo número, para elegir por el nombre de la dueña |
| `UMBRAL_PERSONA_SOLA` | `04e_premios.py` | 90 | premio sin objeto: por debajo, la persona queda vacía en vez de adivinar |

## Sobre `tests/golden/`

Ver `tests/golden/README.md`. Resumen: es un snapshot congelado, no un test. Vale como
verificación **solo si no se re-congela en el mismo commit que cambia el pipeline**.

**Estado al 2026-09-18: desactualizado, y por eso `06_verificar` falla siempre.** El
golden nunca se re-congeló después de que `04d` agregara `lat`/`lon` a `Ciudades` y
`04c` agregara `Imagen` a la vista plana (y, desde 2026-10-12, `05` le suma
`Provincia`, `Lugar en el documento`, `ciudad_id` y las coordenadas de provincia):

```
tabla_normalizada.xlsx        [Ciudades] shape (78, 10) != golden (78, 4)
vista_plana_consolidada.xlsx  [Objetos - Concursos Tucumán] shape (982, 15) != golden (982, 7)
```

Las demás hojas dan OK. Re-congelarlo en un commit propio es una tarea pendiente
(`docs/tareas_pendientes.md`).
