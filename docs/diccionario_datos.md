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
| `fecha_decreto` | texto | fecha del decreto que lo convoca (AAAA-MM-DD o `s/d`) |
| `fecha_inauguracion` | texto | inauguración de la exposición |
| `fecha_fallo` | texto | fecha del fallo del jurado |
| `sede` | texto | local de la exposición |
| `organizacion` | texto | quién lo organizó (gobierno, comisión de damas) |
| `notas_fechas` | texto | de qué fuente sale cada dato (prensa, Archivo Padilla) y sus contradicciones. Ver `docs/relevamiento_prensa_archivo.md` |

### Hoja `Expositoras` (458 filas)
| campo | tipo | descripción |
|---|---|---|
| `persona_id` | int | identificador de persona / institución expositora |
| `Nombre` | texto | nombre tal como se decidió normalizar |
| `Género` | F / M / I | inferido del nombre (correcciones en `decisiones/nombres_expositoras.csv`); I = institución (asilo, escuela, congregación), marca propia en lugar de género (LM 2026-10-28) |

### Hoja `Categorías` (24 filas)
| campo | tipo | descripción |
|---|---|---|
| `categoria_id` | int | identificador |
| `nombre_categoria` | texto | sección del concurso (PAÑUELOS, RANDAS, ALFOMBRAS, …) tal como la imprimió el catálogo |
| `categoria_norm` | texto | sección normalizada dentro de su catálogo: une las secciones que son una misma serie numerada (`09`, `decisiones/categorias.csv`) |
| `criterio` | texto | por qué se normalizó así, con la evidencia del catálogo |
| `estado` | texto | `propuesta` (sin revisar por la dirección) o `validada` |

### Hoja `Ciudades` (77 filas)
| campo | tipo | descripción |
|---|---|---|
| `ciudad_id` | int | identificador |
| `nombre_ciudad` | texto | localidad tal como figura en la fuente histórica |
| `nombre_ciudad_hoy` | texto | topónimo actual equivalente. Sale de `decisiones/coordenadas_ciudades.csv` (lo pone `06`) |
| `nombre_provincia` | texto | provincia actual. Ídem |
| `lat` / `lon` | float | punto de la ciudad. Ídem. 58 de 74 cargadas; el resto queda vacío (nombre ambiguo o desconocido) |
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
| `ciudad_id_catalogo` | int | ciudad que escribió el catálogo cuando `06` pasó la obra a otra: el catálogo dice sólo la provincia ("TUCUMÁN") y la misma expositora tiene obras en una localidad de esa provincia, que pasa a ser `ciudad_id`. Vacío = sin cambio (Julián, 2026-10-28; hoy 53 obras de 7 expositoras) |
| `categoria_id` | int | → `Categorías.categoria_id` |
| `ORDEN` | int | número de orden dentro de la categoría en el catálogo |
| `OBJETO` | texto | descripción del objeto, textual de la fuente |
| `fuente` | texto | hoja del Excel crudo de origen |
| `imagen` | texto | escaneo del catálogo donde figura este objeto. Lo agrega `05_imagenes` cruzando `Paginas_Catalogo` por concurso + categoría + rango de `ORDEN` |
| `fuera_de_concurso` | texto | `sí` si el catálogo dice "(fuera de concurso)": se exhibió pero no compitió. Lo agrega `08_marcas` leyendo `OBJETO`, que no se toca |
| `creacion_autora` | texto | `sí` si el catálogo dice "creación de la autora" (diseño propio). Ídem |
| `foto_album` | texto | foto del álbum de 1915 donde aparece la obra (`data/raw/images/albumes/1915-album-version-2/`). La agrega `05` desde `decisiones/album_1915.csv` |
| `tecnicas` | texto | técnicas de la obra, separadas por `; ` (un subtipo lleva también su técnica general: "Encaje; Encaje de bolillos"). Lectura del proyecto con los términos revisados por LM (`decisiones/tecnicas_materiales.csv`); vacío = sin técnica indicada. La agrega `10` |
| `tecnica_origen` | texto | de dónde sale la técnica: `texto de la obra`, `categoría del catálogo` (el texto no nombra ninguna y se usa la de la sección, `familias_categorias.csv`) o `sin dato`. Ídem |
| `materiales` | texto | materiales que nombra el texto de la obra o la sección del catálogo (Chales de vicuña → Vicuña), separados por `; `. Ídem |

### Hoja `Premios` (102 filas)

La arma `07_premios`: un premio del fallo del jurado de 1915 por fila, cruzado con el
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
| `Imagen del catálogo` | texto | escaneo del catálogo donde figura la obra (no es la foto del álbum) |
| `Estado` | texto | `vinculado`, `fuera de catálogo` o `pendiente` |
| `Vínculo` | texto | cómo se vinculó: `n.º, categoría y nombre`, `n.º y categoría`, `única obra de la expositora en la categoría`, `obra de la expositora con texto parecido` o `decisión a mano` |
| `Nota` | texto | la decisión a mano (`premios_manual.csv`) o, si está pendiente, qué falta resolver |

### Hoja `Fuentes` (6 filas)
| campo | tipo | descripción |
|---|---|---|
| `fuente_id` | int | identificador del documento (1 = catálogo 1915, 2 = fallo del jurado 1915, 3 = catálogo 1916, 4 = diario El Orden, 5 = Archivo Padilla, 6 = nota de Páez de la Torre, 1986) |
| `tipo` | texto | catálogo, fallo de jurado, prensa, archivo personal, … |
| `descripcion` | texto | título del documento |
| `anio` | int | año |
| `repositorio` | texto | dónde se consultó |
| `signatura` | texto | signatura archivística |
| `carpeta_escaneos` | texto | subcarpeta de `data/raw/images/` con el escaneo |
| `notas` | texto | observaciones |

### Hoja `Paginas_Catalogo` (118 filas)

Completada a mano. Dice qué cubre cada imagen escaneada; es el insumo de
`05_imagenes`.

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
| `Género` | `Expositoras.Género` (F, M o I = institución) |
| `Ciudad` | `nombre_ciudad` histórico; si la ciudad es desconocida se muestra la provincia |
| `Provincia` | `nombre_provincia` de esa ciudad |
| `Lugar en el documento` | la procedencia tal como la escribió el catálogo ("SANTIAGO", "SANTIAGO DEL ESTERO"), de `objetos_crudos.csv`. Para cotejar contra la fuente |
| `ciudad_id` | → `Ciudades.ciudad_id`. Dos lugares escritos distinto con el mismo id son la misma fila de `Ciudades` |
| `lat` / `lon` | coordenadas de esa ciudad (vacías si no están cargadas) |
| `lat_provincia` / `lon_provincia` | coordenadas de la capital de su provincia |
| `Dirección de la sede` / `lat_sede` / `lon_sede` | solo para instituciones con sede cargada en `decisiones/sedes_instituciones.csv`: dirección (si la hay) y punto de la sede. `Ciudad`, `lat` y `lon` siguen siendo los de la localidad |
| `Categoría` | nombre de categoría |
| `Categoría normalizada` | `Categorías.categoria_norm` |
| `N.º de orden` | `ORDEN` |
| `Descripción del objeto` | `OBJETO` |
| `Técnicas` | `Objetos.tecnicas` |
| `Técnica según` | `Objetos.tecnica_origen` |
| `Materiales` | `Objetos.materiales` |
| `Fuera de concurso` | `Objetos.fuera_de_concurso` |
| `Creación de la autora` | `Objetos.creacion_autora` |
| `Foto del álbum` | `Objetos.foto_album` |
| `Imagen del catálogo` | escaneo de la página del catálogo donde figura el objeto (`Objetos.imagen`); la foto de la pieza va en `Foto del álbum` |
| `En la prensa` | notas de época de `decisiones/menciones_prensa.csv` que nombran la obra o hablan de su expositora ("sobre la expositora", solo en las obras del concurso del año de la nota): diario, fecha y título, separadas por " \| ". Vacío si no hay |

## `data/processed/redes.xlsx`

La arma `12_redes`: la red de participación (expositoras, instituciones, lugares,
concursos y comisión). Se abre en Gephi o con networkx; el explorador la dibuja en la
pestaña Red.

### Hoja `Nodos` (543 filas)
| campo | descripción |
|---|---|
| `id` | identificador del nodo: `e` + `persona_id` (expositora o institución), `l:…` (lugar), `k1915` / `k1916` (concurso), `m:…` (integrante de la comisión) |
| `tipo` | `expositora`, `institución`, `lugar`, `concurso` o `comisión` |
| `nombre` | nombre normalizado |
| `persona_id` | → `Expositoras.persona_id` (expositoras e instituciones) |
| `concursos` | años en que expuso, separados por `, ` |
| `obras` / `premios` | cantidad de obras y de premios de la expositora; en los lugares, obras que proceden de ahí |
| `lugar` / `provincia` | procedencia de la expositora (la de más obras); en los lugares, sólo la provincia |
| `expositoras` | en los lugares, cuántas expositoras proceden de ahí |

### Hoja `Aristas` (1.190 filas)
| campo | descripción |
|---|---|
| `origen` / `destino` | `id` de los dos nodos |
| `tipo` | `participa` (→ concurso), `procede` (→ lugar), `organiza` (comisión → concurso), `es_expositora` (comisión → su registro de expositora), `mismo_apellido` (expositoras de la misma localidad con un apellido en común), `apellido_comision` (expositora ↔ comisión con un apellido poco frecuente en común) |
| `peso` | obras (en `participa` y `procede`) |
| `detalle` | rol en la comisión, o qué apellido comparten y de qué tipo ("propio = de casada"…) |
| `confianza` | `dato` (lo dicen las fuentes), `media` o `baja` (hipótesis de parentesco por apellido; baja si 5 o más registros llevan ese apellido) |

### Hoja `Grupos` (61 filas)
Componentes conexas de las aristas `mismo_apellido`: `grupo`, `personas`, `apellidos`,
`lugar`, `confianza`, `persona_ids` (separados por `;`) e `integrantes`. Es una pista de
parentesco, no un dato.

## `data/interim/duplicados_expositoras_candidatos.xlsx`

Pares candidatos a fusión que genera `02_candidatos.py` (fuzzy matching, `UMBRAL = 80`),
para revisar a mano.

| campo | descripción |
|---|---|
| `id_A`, `nombre_A` / `id_B`, `nombre_B` | los dos registros del par |
| `score` | mayor ratio obtenido (0–100) |
| `tipo` | `exacto_norm`, `alta`, `media`, `media (sin partículas)`, `compatible (inicial / palabra agregada)` |
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

Las fusiones de expositoras que aplica `03_fusiones.py` (55 filas).

| campo | descripción |
|---|---|
| `mantener` | `persona_id` que sobrevive |
| `descartar` | uno o más `persona_id` a fusionar, separados por espacio |
| `origen` | `decidida` (el comentario dice qué lado queda), `sin_lado` (no lo dice; se conserva el lado con más objetos), `cluster` (grupo de 3+ ids) |
| `nota` | el comentario de la revisión que originó la decisión |

## `data/interim/decisiones/menciones_prensa.csv`

Qué obras, expositoras y lugares de la base comenta la prensa de época (14 filas, armada
a mano a partir de las hojas "no …" del crudo; ver `docs/relevamiento_prensa_archivo.md`).
La lee `14_explorador`: cada mención aparece en la ficha de la persona, en sus obras
("· En la prensa") y en el panel del lugar en el mapa.

| campo | descripción |
|---|---|
| `fuente_id` | → `Fuentes.fuente_id` |
| `fecha` | fecha de la nota (AAAA-MM-DD) |
| `titulo` | título de la nota |
| `persona_id` | → `Expositoras.persona_id` (vacío si la nota habla de un lugar) |
| `objeto_id` | → `Objetos.objeto_id`; varios separados por `;` si la nota no permite elegir entre dos |
| `ciudad_id` | → `Ciudades.ciudad_id`, para menciones de lugares; varios separados por `;` |
| `nivel` | `obra`, `persona` o `lugar`: a qué se puede atar la mención con seguridad |
| `cita` | el pasaje, textual de la transcripción |
| `nota` | cómo se identificó la obra o la persona, y dudas |
| `mostrar` | `no` para una mención descartada en la revisión (queda registrada, pero el explorador no la muestra); vacío = se muestra |

## `data/interim/decisiones/genero_solo_fallo.csv`

Género de quienes figuran solo en el fallo del jurado de 1915 (premio sin obra en el
catálogo) y por eso no tienen fila en la hoja `Expositoras` (5 filas). Se infiere del
nombre, como el resto de la base. La lee `14_explorador` para el filtro Expositores.

| campo | descripción |
|---|---|
| `nombre_en_fallo` | nombre tal como figura en el fallo |
| `genero` | `F`, `M` o `I` (institución) |
| `nota` | de dónde sale |

## `data/interim/decisiones/accesit_fallo.csv`

Premios que el fallo de 1915 llama accésit fuera de la sección Accésit (4 filas: los de
$ 25 de Crochet e Irlanda, p. 20, DSCN5256). Con los 8 de esa sección suman 12. La lee
`14_explorador`, que los muestra como «Accésit» sin cambiar su sección del fallo; si el
nombre no coincide con el del `premio_id`, avisa y no lo marca.

| campo | descripción |
|---|---|
| `premio_id` | `premio_id` de la hoja `Premios` |
| `nombre_en_fallo` | nombre tal como figura en el fallo, para controlar que el id sea el correcto |
| `nota` | de dónde sale |

## `data/interim/decisiones/comisiones.csv`

Integrantes de la comisión organizadora y jurado de cada concurso (25 filas, cargadas a
mano del catálogo y el fallo de 1915, del catálogo de 1916 y de El Orden). Una fila por
persona, año y rol. La leen `12_redes` y `14_explorador`.

| campo | descripción |
|---|---|
| `anio` | 1915 o 1916 |
| `nombre` | nombre normalizado (con tildes; la forma más completa entre las fuentes) |
| `nombre_en_fuente` | como lo escribe la fuente |
| `rol` | presidenta, vicepresidenta, secretaria, secretaria general, secretaria de sección, vocal, integrante de la comisión |
| `seccion` | para las secretarias de sección de 1916 |
| `fuente` | de dónde sale el dato |
| `persona_id` | → `Expositoras.persona_id`, si también expuso (hoy sólo Isabel Bascary de Acuña Zavalía, 58) |
| `nota` | aclaraciones |
