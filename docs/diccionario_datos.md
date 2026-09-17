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

### Hoja `Expositoras` (471 filas)
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
| `nombre_ciudad_hoy` | texto | topónimo actual equivalente (decisión manual) |
| `nombre_provincia` | texto | provincia actual (decisión manual) |

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

### Hoja `Premios` (104 filas)

Columnas 1–8: transcripción del fallo del jurado, casi textual.
Columnas 9–14: agregadas por `03b_premios.py`.
Columnas 15–17: anotación manual (estudiante y dirección).

| campo | tipo | descripción |
|---|---|---|
| `PREMIOS` | texto | premio otorgado (monto / mención) |
| `NOMBRE` | texto | expositora premiada, según el fallo |
| `CIUDAD` | texto | localidad según el fallo |
| `PROVINCIA` | texto | provincia según el fallo |
| `OBJETO` | texto | objeto premiado |
| `CATEGORÍA` | texto | categoría del premio |
| `OBSERVACIONES` | texto | notas del relevamiento |
| `NÚM` | texto | nº de orden del objeto en el catálogo (puede ser "s/d" o un rango) |
| `persona_id` | int | → `Expositoras.persona_id`, resuelto por nombre (fuzzy) |
| `persona` | texto | nombre de esa expositora en el catálogo, para control visual |
| `persona_score` | float | ratio 0–100 del match de nombre |
| `objeto_id` | texto | → `Objetos.objeto_id`; puede traer varios separados por coma, o vacío |
| `objeto_match` | texto | cómo se resolvió el cruce: `num+categoria`, `num+categoria+persona`, … El sufijo `+persona` solo aparece si el filtro por persona se aplicó de verdad (ver bitácora, 2026‑09‑14) |
| `revisar` | texto | `X` si el cruce quedó dudoso |
| `Mis comentarios` | texto | anotación del estudiante |
| `Coment LM` | texto | anotación de la dirección |
| `Hecho o revisado` | texto | estado de la revisión conjunta |

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
| `Categoría` | nombre de categoría |
| `N.º de orden` | `ORDEN` |
| `Descripción del objeto` | `OBJETO` |

## `data/interim/duplicados_expositoras_candidatos.xlsx`

Pares candidatos a fusión que genera `03_candidatos.py` (fuzzy matching, `UMBRAL = 87`),
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

Las columnas `Hecho` y `Comentarios` son **insumo humano**: el script las relee y las
conserva emparejadas por `(id_A, id_B)`. Regenerar el archivo nunca las pisa ni elimina
pares ya listados.

`data/interim/revision_duplicados.xlsx` es la versión anterior de esta tabla, ya anotada;
se conserva porque es la fuente de las decisiones que hoy están en
`decisiones/fusiones_expositoras.csv`.

## `data/interim/decisiones/fusiones_expositoras.csv`

Las 42 fusiones de expositoras que aplica `04_aplicar_dedup.py`.

| campo | descripción |
|---|---|
| `mantener` | `persona_id` que sobrevive |
| `descartar` | uno o más `persona_id` a fusionar, separados por espacio |
| `origen` | `decidida` (el comentario dice qué lado queda), `sin_lado` (no lo dice; se conserva el lado con más objetos), `cluster` (grupo de 3+ ids) |
| `nota` | el comentario de la revisión que originó la decisión |
