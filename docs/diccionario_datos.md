# Diccionario de datos

## `data/processed/tabla_normalizada.xlsx`

### Hoja `Concursos`
| campo | tipo | descripción |
|---|---|---|
| `concurso_id` | int | identificador (1 = 1915, 2 = 1916) |
| `anio` | int | año de realización |
| `nombre` | texto | nombre del concurso |
| `lugar` | texto | ciudad sede |

### Hoja `Expositoras`
| campo | tipo | descripción |
|---|---|---|
| `persona_id` | int | identificador de persona / institución expositora |
| `Nombre` | texto | nombre tal como se decidió normalizar |
| `Género` | F / M | inferido del nombre; instituciones marcadas F por convención (revisar) |

### Hoja `Categorías`
| campo | tipo | descripción |
|---|---|---|
| `categoria_id` | int | identificador |
| `nombre_categoria` | texto | sección del concurso (PAÑUELOS, RANDAS, ALFOMBRAS, …) |

### Hoja `Ciudades`
| campo | tipo | descripción |
|---|---|---|
| `ciudad_id` | int | identificador |
| `nombre_ciudad` | texto | localidad tal como figura en la fuente histórica |
| `nombre_ciudad_hoy` | texto | topónimo actual equivalente (decisión manual) |
| `nombre_provincia` | texto | provincia actual (decisión manual) |

### Hoja `Objetos`
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

### Hoja `Premios`
| campo | tipo | descripción |
|---|---|---|
| `PREMIOS` | texto | premio otorgado (monto / mención) |
| `NOMBRE` | texto | expositora premiada (sin normalizar contra `Expositoras` aún) |
| `CIUDAD` | texto | localidad según el fallo |
| `PROVINCIA` | texto | provincia según el fallo |
| `OBJETO` | texto | objeto premiado |
| `CATEGORÍA` | texto | categoría del premio |
| `OBSERVACIONES` | texto | notas del relevamiento |
| `NÚM` | texto | número de orden del objeto en el catálogo (puede ser "s/d" o rango) |

## `data/processed/vista_plana_tabla_consolidada.xlsx`

Hoja `Objetos - Concursos Tucumán`: `Objetos` con los identificadores resueltos a
nombres. Orden: por Concurso, Categoría (alfabético), Ciudad, N.º de orden.

| campo | descripción |
|---|---|
| `Concurso` / `Año` | del concurso |
| `Expositora/Expositor` | nombre normalizado |
| `Ciudad` | `nombre_ciudad` histórico |
| `Categoría` | nombre de categoría |
| `N.º de orden` | `ORDEN` |
| `Descripción del objeto` | `OBJETO` |

## `data/interim/revision_duplicados.xlsx`

Pares candidatos a fusión, generados por fuzzy matching y revisados a mano.

| campo | descripción |
|---|---|
| `id_A`, `nombre_A` | primer registro del par |
| `id_B`, `nombre_B` | segundo registro del par |
| `Hecho` | True = confirmado como misma entidad; False = se deja separado (ver comentario) |
| `Comentarios` | criterio aplicado / duda pendiente |
