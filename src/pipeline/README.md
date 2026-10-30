# Pipeline

Reconstruye, en código, el camino desde el Excel crudo hasta las tablas normalizadas.
**Esta es la descripción canónica del flujo**: el README de la raíz apunta acá en vez
de repetirla.

Correr todo: `python run_pipeline.py` (desde la raíz). Desde una etapa en adelante:
`python run_pipeline.py 04`. Una etapa suelta: `python src/pipeline/01_ingesta.py`.

| etapa | entrada | salida | estado |
|---|---|---|---|
| `01_ingesta` | `data/raw/TUCUMÁN text 1915-16 DATOS.xlsx` | `data/interim/objetos_crudos.csv` (981 objetos; separa las filas explotadas de 1916). Aplica `decisiones/objetos_texto_override.csv` y deja los textos sin espacios de más (`limpiar_texto`, `_util.py`) | funciona |
| `03_candidatos` | `data/interim/tabla_normalizada_manual.xlsx` (Expositoras, Ciudades, Objetos) | `data/interim/duplicados_expositoras_candidatos.xlsx` — 141 filas (135 detectadas hoy + 6 conservadas de corridas anteriores), con `Hecho`/`Comentarios` para anotar. Conserva las anotaciones y los pares que ya figuraban. Al final imprime cuántos quedan **sin fusionar y sin revisar**: hoy 48, contando pares con un id que ya se fusionó por otro camino (ver `docs/tareas_pendientes.md`) | funciona |
| `04_aplicar_dedup` | `data/interim/tabla_normalizada_manual.xlsx` + `decisiones/fusiones_expositoras.csv`, `nombres_expositoras.csv`, `fusiones_ciudades.csv`, `separaciones_ciudades.csv` | `data/interim/tabla_normalizada_dedup.xlsx`. Antes de aplicar nada, limpia los espacios de más en todas las hojas (hoy: 8 nombres, 21 objetos, 7 celdas de Premios, 1 de Paginas_Catalogo). 55 decisiones en el CSV, **54 aplicadas**, 519 → 458 expositoras; 1 fusión de ciudades (50 → 5). Dos ids a descartar ya no existen en la tabla manual (67 y 117) y el script los avisa; la fila `76,67` queda sin efecto por eso | funciona |
| `04b_titulo_nombres` | tabla_normalizada_dedup | `data/processed/tabla_normalizada.xlsx` (nombres ALLCAPS → Título) | funciona |
| `04c_vincular_imagenes` | tabla_normalizada + hoja `Paginas_Catalogo` | tabla_normalizada con la columna `Objetos.imagen` — 981/981 objetos con imagen | funciona |
| `04d_coordenadas` | tabla_normalizada + `decisiones/coordenadas_ciudades.csv` | tabla_normalizada con la ubicación de cada ciudad tomada del CSV: `nombre_ciudad_hoy`, `nombre_provincia`, `lat`/`lon`, `lat_provincia`/`lon_provincia`, `precision`, `nota` — 61/77 ciudades con coordenada, 70/77 con punto de provincia. En `Objetos`, las obras con sólo la provincia pasan a la localidad de la misma expositora en esa provincia (`ciudad_id_catalogo` guarda la original) | funciona |
| `04e_premios` | `tabla_normalizada_dedup.xlsx` (Premios de la tabla manual) + tabla_normalizada (Expositoras, Objetos) + `decisiones/premios_manual.csv` | tabla_normalizada con la hoja `Premios` curada: un premio por fila, con su obra del catálogo, `Estado` (vinculado / fuera de catálogo / pendiente), `Vínculo` y `Nota` — 102 premios: 89 vinculados y 13 fuera de catálogo | funciona |
| `04f_marcas_objetos` | tabla_normalizada (Objetos) | tabla_normalizada con `Objetos.fuera_de_concurso` (2) y `Objetos.creacion_autora` (12), leídas del texto del catálogo, que no se toca | funciona |
| `04g_categorias` | tabla_normalizada (Categorías) + `decisiones/categorias.csv` | tabla_normalizada con `Categorías.categoria_norm` (24 secciones → 22: une Chales de vicuña con Chales y echarpes y Jergones con Jergones y sobrepelos, que son una misma serie numerada), `criterio` y `estado`. `nombre_categoria` no se toca. Todo en *propuesta* hasta que lo revise LM | funciona |
| `04h_tecnicas_materiales` | tabla_normalizada (Objetos) + `decisiones/tecnicas_materiales.csv` y `familias_categorias.csv` | tabla_normalizada con `Objetos.tecnicas`, `tecnica_origen` (texto de la obra / categoría del catálogo / sin dato) y `materiales`: 559 obras con técnica en el texto, 127 por la categoría y 295 sin dato; 252 con material. Las reglas están en `_tecnicas.py`, que usa también `05c`, así la base y el explorador dicen lo mismo | funciona |
| `05_vista_plana` | tabla_normalizada | `data/processed/vista_plana_tabla_consolidada.xlsx` (981 filas, incluye `Género`, `lat`/`lon`, `Técnicas`, `Técnica según`, `Materiales` e `Imagen del catálogo`) | funciona |
| `05a_redes` | tabla_normalizada + `decisiones/comisiones.csv` | `data/processed/redes.xlsx` (hojas Nodos, Aristas y Grupos, que lee `05c`: expositoras, instituciones, lugares, concursos y comisión; 543 nodos) y `outputs/redes.md`: quiénes repitieron en 1915 y 1916 (32), expositoras por lugar, grupos con el mismo apellido en el mismo lugar y apellidos en común con la comisión. Las aristas de apellido son hipótesis de parentesco, con `confianza` media o baja | funciona |
| `05b_mapa` | tabla_normalizada | `outputs/mapa_procedencias.html` (folium): capa de ciudades (un círculo por localidad actual: 53 puntos, 817 objetos; el popup avisa si la ubicación es tentativa) y capa "sólo provincia" en la capital, con borde punteado como en el explorador (8 puntos, 126 objetos); 38 objetos sin ubicar. Los ids de folium se reemplazan por correlativos, así dos corridas dan el mismo archivo. Antes lo exportaba `notebooks/04_eda.ipynb`, que ahora sólo lo muestra | funciona |
| `05c_explorador` | tabla_normalizada (incluida la hoja Premios) + `objetos_crudos.csv` + `decisiones/familias_categorias.csv`, `tecnicas_materiales.csv`, `menciones_prensa.csv` y `comisiones.csv` + `redes.xlsx` | `outputs/explorador.html`: explorador web autocontenido en cuatro pestañas: mapa, análisis (cifras, los dos concursos, procedencia, técnicas, expositoras y premios, cada gráfico con su tabla) y fichas de expositoras con la fuente de cada obra (catálogo, página impresa y escaneo, de `Paginas_Catalogo`); descarga de la base y del diccionario en CSV; prensa de época (`decisiones/menciones_prensa.csv`) en fichas, obras y lugares; comparación 1915/1916 (hoja `Concursos`) y comisión organizadora y jurado (`decisiones/comisiones.csv`), dónde están los documentos (hoja `Fuentes`), grupos con el mismo apellido en el mismo lugar (hoja `Grupos` de `redes.xlsx`, `05a`) en Análisis y en las fichas, la pestaña Red con el grafo completo (hojas Nodos y Aristas; sigma.js y graphology desde CDN), y lo que el archivo no dice. Filtros por premio, técnica, material, género (`Expositoras.Género`), provincia, año y texto. Todo sale de la plantilla `plantillas/explorador.template.html`. 994 obras = 981 objetos + 13 premios de 1915 sin obra en el catálogo (fuera de catálogo). Técnicas y materiales con las mismas reglas que `04h` (`_tecnicas.py`). La procedencia se agrupa por provincia; zonas y tipos de obra quedaron fuera el 28/10 hasta que los revise LM | funciona |
| `06b_controles` | tabla_normalizada + `objetos_crudos.csv` + candidatos | `outputs/controles_calidad.md`: errores típicos de los catálogos (personas, lugares, números de orden y páginas, premios, transcripción), con id y página escaneada. No corrige nada; lo ya decidido no vuelve a aparecer | funciona |
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

Ninguna etapa lee la salida de una posterior. Verificado otra vez el 2026-10-25: corriendo
`python run_pipeline.py` en una copia limpia del repo, las salidas quedan **idénticas
celda por celda** a las commiteadas (cambia sólo la metadata del zip de cada `.xlsx`,
así que `git status` las marca como modificadas igual).

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
  (`persona_id`, `nombre`, `nota`, `genero`), p. ej. la variante entre corchetes acordada
  con Larisa ("Facunda Cerone [Coronel]"). `genero` (F / M) corrige el de la tabla
  manual; un `nombre` vacío deja el nombre como está. Lo aplica `04_aplicar_dedup`.
- `fusiones_ciudades.csv` — mismo lugar cargado con dos `ciudad_id` (mismo formato que
  las fusiones de expositoras). Lo aplica `04_aplicar_dedup`; el texto del catálogo
  sigue visible en la vista plana ("Lugar en el documento").
- `separaciones_ciudades.csv` — al revés que una fusión: un `ciudad_id` que junta
  envíos de lugares distintos se parte; se crea `ciudad_id_nueva` y los `objetos`
  listados pasan a ella. Lo aplica `04_aplicar_dedup`. Hoy: "CHACO" (53) → Misión
  Franciscana de Nueva Pompeya (82).
- `album_1915.csv` — transcripción de LM de las fotos del álbum de 1915 (foto, n.º,
  descripción, posición en la foto) y el `objeto_id` de cada pieza, que encontramos
  cruzando n.º y descripción con el catálogo (13 de 14). Lo lee `04c`, que agrega
  `Objetos.foto_album`.
- `objetos_texto_override.csv` — celdas de texto que la investigadora corrigió a mano
  respecto del catálogo (erratas, singular/plural, mayúsculas) y números de orden
  corregidos contra el escaneo (objeto 17: 17 → 19). Lo aplica `01_ingesta`.
- `premios_manual.csv` — correcciones al cruce Premios ↔ Objetos. Acepta
  `objeto_id = "ninguno"` para forzar que un premio quede sin objeto y
  `objeto_id = "pendiente"` para dejarlo marcado como duda abierta.
- `coordenadas_ciudades.csv` — la única fuente de la ubicación de cada ciudad
  (`ciudad_id`): `nombre_ciudad_hoy`, `nombre_provincia`, `lat`/`lon` (cargadas a mano
  por la investigadora, Google Maps), `lat_provincia`/`lon_provincia` (capital),
  `precision` y `nota`. `04d` pisa con esto la copia de la tabla manual. 61/77 con
  punto de ciudad; el resto queda vacío (nombre ambiguo o desconocido).
- `categorias.csv` — nombre normalizado de cada sección dentro de su catálogo
  (`categoria_norm`), con el `criterio` y su evidencia (numeración continua, contenido de
  las obras) y un `estado` (hoy todo `propuesta`). Lo aplica `04g`.
- `familias_categorias.csv` — por categoría, la técnica que se asume cuando el texto del
  objeto no nombra ninguna (`tecnica_por_categoria`), el material que nombra la sección
  (`material_por_categoria`: Chales de vicuña, Raffia imitación con hojas de caña), que
  usan `04h` y `05c` (vía `_tecnicas.py`), y un tipo
  de obra (`familia`) que propuso el proyecto sin respaldo en las fuentes. Desde el 28/10
  el explorador no usa la `familia`: queda para revisar con LM.
- `zonas_ciudades.csv` — zona de cada `ciudad_id`, propuesta por el proyecto a partir de
  la provincia y la distancia a la capital (columna `criterio`). Desde el 28/10 el
  explorador no la usa: queda para revisar con LM.
- `tecnicas_materiales.csv` — términos de técnica, proceso y material que aparecen en
  los textos de las obras, con la revisión de LM del 28/10 (`validacion_LM`). La leen
  `04h` y `05c` (vía `_tecnicas.py`): `clave` (vacía = no se usa), `etiqueta`, `grupo` (técnica general de
  un subtipo), `patron` y `excepto` (expresiones regulares sobre el texto sin tildes y en
  minúsculas). `n_obras` cuenta las obras que cumplen la regla.
- `menciones_prensa.csv` — qué obras, expositoras y lugares comenta la prensa de época,
  con la cita textual (ver `docs/relevamiento_prensa_archivo.md`). La lee `05c`: la cita
  aparece en la ficha de la persona, en sus obras y en el panel del lugar.
- `comisiones.csv` — integrantes de la comisión organizadora y jurado de cada concurso.
  La leen `05a` (nodos y aristas de comisión) y `05c`.

## Parámetros

Los del pipeline son umbrales de parecido de nombres (0–100, `rapidfuzz`). No hay modelos
entrenados. La única aleatoriedad es la posición inicial de los nodos en la pestaña Red
del explorador: ForceAtlas2 (900 iteraciones; 600 en la red de lugares y técnicas) parte
de posiciones con semilla fija (11; 5 en la red de lugares y técnicas), así el dibujo es el mismo en cada apertura. Cada
cambio queda en `docs/bitacora.md`.

| parámetro | dónde | valor | para qué |
|---|---|---|---|
| `UMBRAL` | `03_candidatos.py` | 80 | parecido mínimo del nombre entero para proponer un par como duplicado (era 87) |
| `UMBRAL_APELLIDO` | `03_candidatos.py` | 75 | en la regla de nombres "compatibles", parecido mínimo del apellido |
| `UMBRAL_NOMBRE` | `04e_premios.py` | 60 | el dueño del objeto tiene que parecerse al nombre del premio para aceptar el vínculo |
| `UMBRAL_ELEGIR` | `04e_premios.py` | 80 | con varios objetos con el mismo número, para elegir por el nombre de la dueña |
| `UMBRAL_PERSONA_SOLA` | `04e_premios.py` | 90 | premio sin objeto: por debajo, la persona queda vacía en vez de adivinar |
