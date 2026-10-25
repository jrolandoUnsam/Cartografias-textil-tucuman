# Diccionario de datos

## `data/processed/tabla_normalizada.xlsx`

8 hojas. `Concursos`, `Expositoras`, `Categorías`, `Ciudades`, `Objetos` y `Premios`
son el modelo relacional; `Fuentes` y `Paginas_Catalogo` describen de qué documento y
de qué página salió cada registro.

### Hoja `Concursos` (2 filas)
| campo | tipo | descripción |
|---|---|---|
| `concurso_id` | int | identificador (1 = 1915, 2 = 1916) |
| `anio` | int | año de realización |
| `nombre` | texto | nombre del concurso |
| `lugar` | texto | ciudad sede |

### Hoja `Expositoras` (458 filas)
| campo | tipo | descripción |
|---|---|---|
| `persona_id` | int | identificador de persona / institución expositora |
| `Nombre` | texto | nombre tal como se decidió normalizar |
| `Género` | F / M | inferido del nombre; instituciones marcadas F por convención (revisar) |

### Hoja `Categorías` (24 filas)
| campo | tipo | descripción |
|---|---|---|
| `categoria_id` | int | identificador |
| `nombre_categoria` | texto | sección del concurso (PAÑUELOS, RANDAS, ALFOMBRAS, …) |

### Hoja `Ciudades` (77 filas)
| campo | tipo | descripción |
|---|---|---|
| `ciudad_id` | int | identificador |
| `nombre_ciudad` | texto | localidad tal como figura en la fuente histórica |
| `nombre_ciudad_hoy` | texto | topónimo actual equivalente. Sale de `decisiones/coordenadas_ciudades.csv` (lo pone `04d`) |
| `nombre_provincia` | texto | provincia actual. Ídem |
| `lat` / `lon` | float | punto de la ciudad. Ídem. 53 de 77 cargadas; el resto queda vacío (nombre ambiguo o desconocido) |
| `lat_provincia` / `lon_provincia` | float | punto de la capital de la provincia, para ubicar a nivel provincia lo que no tiene ciudad o no tiene punto seguro (pedido de Larisa, 2026-10). Ídem |
| `precision` | texto | vacío = ubicación segura; `tentativa` si no lo es. Ídem |
| `nota` | texto | por qué se decidió así (p. ej. `LM 9-10: …`). Ídem |

### Hoja `Objetos` (981 filas)
| campo | tipo | descripción |
|---|---|---|
| `objeto_id` | int | identificador (orden de aparición en el Excel crudo) |
| `expositora_id` | int | → `Expositoras.persona_id` |
| `concurso_id` | int | → `Concursos.concurso_id` |
| `ciudad_id` | int | → `Ciudades.ciudad_id` |
| `categoria_id` | int | → `Categorías.categoria_id` |
| `ORDEN` | int | número de orden dentro de la categoría en el catálogo |
| `OBJETO` | texto | descripción del objeto, textual de la fuente |
| `fuente` | texto | hoja del Excel crudo de origen |
| `imagen` | texto | escaneo del catálogo donde figura este objeto. Lo agrega `04c_vincular_imagenes` cruzando `Paginas_Catalogo` por concurso + categoría + rango de `ORDEN` |
| `fuera_de_concurso` | texto | `sí` si el catálogo dice "(fuera de concurso)": se exhibió pero no compitió. Lo agrega `04f_marcas_objetos` leyendo `OBJETO`, que no se toca |
| `creacion_autora` | texto | `sí` si el catálogo dice "creación de la autora" (diseño propio). Ídem |
| `foto_album` | texto | foto del álbum de 1915 donde aparece la obra (`data/raw/images/albumes/1915-album-version-2/`). La agrega `04c` desde `decisiones/album_1915.csv` |

### Hoja `Premios` (102 filas)

La arma `04e_premios`: un premio del fallo del jurado de 1915 por fila, cruzado con el
catálogo y curado. Las decisiones a mano están en `decisiones/premios_manual.csv`. Las
columnas de trabajo de la revisión (`persona_score`, `revisar`, "Mis comentarios",
"Coment LM", …) quedan en la tabla manual y en las revisiones de LM de `data/raw`; acá
no van. Los renglones del fallo que no premian a nadie ("Primer premio desierto") no
son filas.

| campo | tipo | descripción |
|---|---|---|
| `premio_id` | int | número de fila (0-based) de la hoja Premios de la tabla manual; es la clave de `premios_manual.csv` |
| `Premio` | texto | premio otorgado, textual del fallo (monto / tipo) |
| `Nombre en el fallo` | texto | expositora premiada, como la escribe el fallo |
| `Ciudad en el fallo` | texto | localidad según el fallo |
| `Provincia en el fallo` | texto | provincia según el fallo |
| `Categoría del fallo` | texto | categoría del premio, textual (vacía cuando el fallo no la repite) |
| `Sección del fallo` | texto | la sección a la que pertenece el premio: la categoría, o la última que nombró el fallo; tras DESHILADO, "Accésit" |
| `Objeto en el fallo` | texto | objeto premiado, según el fallo |
| `N.º` | texto | n.º de orden que cita el fallo (puede ser "s/d" o un rango) |
| `Observaciones` | texto | notas del relevamiento ("HAY FOTO…", "fuera de catálogo") |
| `persona_id` | int | → `Expositoras.persona_id`; vacío si no está en el catálogo |
| `Expositora` | texto | nombre normalizado de esa expositora |
| `objeto_id` | texto | → `Objetos.objeto_id`; varios separados por `;` si el premio abarca un rango (ej. `35;36;37;38;39`) |
| `Obra en el catálogo` | texto | descripción de la(s) obra(s) en el catálogo, separadas por una barra vertical |
| `Categoría del catálogo` | texto | categoría del catálogo de esa obra |
| `N.º en el catálogo` | texto | n.º de orden en el catálogo |
| `Imagen` | texto | escaneo del catálogo donde figura la obra |
| `Estado` | texto | `vinculado`, `fuera de catálogo` o `pendiente` |
| `Vínculo` | texto | cómo se vinculó: `n.º, categoría y nombre`, `n.º y categoría`, `única obra de la expositora en la categoría`, `obra de la expositora con texto parecido` o `decisión a mano` |
| `Nota` | texto | la decisión a mano (`premios_manual.csv`) o, si está pendiente, qué falta resolver |

### Hoja `Fuentes` (4 filas)
| campo | tipo | descripción |
|---|---|---|
| `fuente_id` | int | identificador del documento (1 = catálogo 1915, 2 = fallo del jurado 1915, 3 = catálogo 1916) |
| `tipo` | texto | catálogo, fallo de jurado, … |
| `descripcion` | texto | título del documento |
| `anio` | int | año |
| `repositorio` | texto | dónde se consultó |
| `signatura` | texto | signatura archivística |
| `carpeta_escaneos` | texto | subcarpeta de `data/raw/images/` con el escaneo |
| `notas` | texto | observaciones |

### Hoja `Paginas_Catalogo` (118 filas)

Completada a mano. Dice qué cubre cada imagen escaneada; es el insumo de
`04c_vincular_imagenes`.

| campo | tipo | descripción |
|---|---|---|
| `fuente_id` | int | → `Fuentes.fuente_id` |
| `imagen` | texto | nombre del archivo escaneado |
| `pagina_impresa` | texto | número de página impreso en el documento |
| `categoria_o_seccion` | texto | sección del catálogo que aparece en esa página |
| `primera_persona` / `ultima_persona` | texto | primera y última expositora de la página (control) |
| `orden_desde` / `orden_hasta` | int | rango de `ORDEN` que cubre la página |
| `notas` | texto | observaciones |

## `data/processed/vista_plana_tabla_consolidada.xlsx`

Hoja `Objetos - Concursos Tucumán` (981 filas): `Objetos` con los identificadores
resueltos a nombres.

Orden de filas: **Año → Categoría (alfabético) → Expositora (alfabético, sensible a
mayúsculas)**. Dentro de un mismo grupo se conserva el orden del catálogo
(`objeto_id`), no el N.º de orden.

| campo | descripción |
|---|---|
| `Concurso` / `Año` | del concurso |
| `Expositora/Expositor` | nombre normalizado |
| `Ciudad` | `nombre_ciudad` histórico; si la ciudad es desconocida se muestra la provincia |
| `Provincia` | `nombre_provincia` de esa ciudad |
| `Lugar en el documento` | la procedencia tal como la escribió el catálogo ("SANTIAGO", "SANTIAGO DEL ESTERO"), de `objetos_crudos.csv`. Para cotejar contra la fuente |
| `ciudad_id` | → `Ciudades.ciudad_id`. Dos lugares escritos distinto con el mismo id son la misma fila de `Ciudades` |
| `lat` / `lon` | coordenadas de esa ciudad (vacías si no están cargadas) |
| `lat_provincia` / `lon_provincia` | coordenadas de la capital de su provincia |
| `Categoría` | nombre de categoría |
| `N.º de orden` | `ORDEN` |
| `Descripción del objeto` | `OBJETO` |
| `Fuera de concurso` | `Objetos.fuera_de_concurso` |
| `Creación de la autora` | `Objetos.creacion_autora` |
| `Foto del álbum` | `Objetos.foto_album` |
| `Imagen` | escaneo del catálogo donde figura el objeto (`Objetos.imagen`) |

## `data/interim/duplicados_expositoras_candidatos.xlsx`

Pares candidatos a fusión que genera `03_candidatos.py` (fuzzy matching, `UMBRAL = 80`),
para revisar a mano.

| campo | descripción |
|---|---|
| `id_A`, `nombre_A` / `id_B`, `nombre_B` | los dos registros del par |
| `score` | mayor ratio obtenido (0–100) |
| `tipo` | `exacto_norm`, `alta`, `media`, `media (sin partículas)` |
| `ciudades_A/B`, `misma_ciudad` | contexto geográfico de cada lado |
| `concursos_A/B`, `n_obj_A/B`, `id_objetos_A/B` | contexto documental de cada lado |
| `ya_fusionada` | el par ya está resuelto en `decisiones/fusiones_expositoras.csv` |
| `detectado` | `True` si la detección de la última corrida lo propuso; `False` si se conserva de una corrida anterior (p. ej. porque los nombres ya se unificaron) |
| `Hecho` | True = misma entidad; False = se deja separado (ver comentario) |
| `Comentarios` | criterio aplicado / duda pendiente |
| `origen_comentario` | de dónde viene el comentario: `candidatos` (anotado en este mismo archivo) o `revision_duplicados` (heredado de la semilla) |

Las columnas `Hecho` y `Comentarios` son **insumo humano**: el script las relee y las
conserva emparejadas por `(id_A, id_B)`. Regenerar el archivo nunca las pisa ni elimina
pares ya listados.

`data/interim/revision_duplicados.xlsx` es la versión anterior de esta tabla, ya anotada;
se conserva porque es la fuente de las decisiones que hoy están en
`decisiones/fusiones_expositoras.csv`.

## `data/interim/decisiones/fusiones_expositoras.csv`

Las fusiones de expositoras que aplica `04_aplicar_dedup.py` (55 filas).

| campo | descripción |
|---|---|
| `mantener` | `persona_id` que sobrevive |
| `descartar` | uno o más `persona_id` a fusionar, separados por espacio |
| `origen` | `decidida` (el comentario dice qué lado queda), `sin_lado` (no lo dice; se conserva el lado con más objetos), `cluster` (grupo de 3+ ids) |
| `nota` | el comentario de la revisión que originó la decisión |
