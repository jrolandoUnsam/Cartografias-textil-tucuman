# Bitácora de decisiones

Registro cronológico de decisiones de diseño, criterios de normalización y fuentes
descartadas. Cada entrada: fecha, decisión, motivo.

## 2026-09 — Reconstrucción del pipeline

- **El Excel crudo (`data/raw/…`) no se toca.** Todo el procesamiento pasa a código
  reproducible. El estado actual de `data/processed/` y `data/interim/` se toma como
  objetivo a reproducir ("golden", copiado en `tests/golden/`).
- **`revision_duplicados.xlsx` es una salida anotada a mano.** El pipeline genera los
  pares candidatos (fuzzy matching); las columnas `Hecho` y `Comentarios` son insumo
  humano. Al regenerar, solo se agregan pares nuevos: nunca se pisan anotaciones.
- **Tablas de decisión manuales** (`data/interim/decisiones/`): `nombre_ciudad_hoy` y
  `nombre_provincia` de cada localidad histórica; unificaciones de categorías entre
  1915 y 1916. No son derivables del crudo.
- **`objeto_id`** sigue el orden de fila del Excel crudo: primero la hoja
  "1915 1er concurso EXPOS", después "1916 Concurso Tejidos".
- **Filas "explotadas" (1916):** una fila con orden `"2, 3, 4"` y objeto
  `"2, Frazada…; 3, Frazada…; 4, Frazada…"` se separa en una fila por objeto.

## Criterios de normalización de nombres de personas (pendiente de completar)

- Cuando el nombre aparece con y sin "de" (ej. `Ana Tactagi` / `Ana de Tactagi`), se
  conserva la forma **con** "de" (aporta más información).
- Dudas de transcripción (`J` vs `I`, `Panci` vs `Panei`, `Barrera` vs `Barrero`):
  se dejan sin fusionar (`Hecho = False`) y se anota el motivo.

## 2026-09-14 — Bug en el vínculo Premios ↔ Objetos (`03b_premios.py`)

- **Etiqueta `objeto_match` engañosa.** Cuando el cruce por `NÚM` + categoría
  encontraba un único objeto candidato, la etiqueta `"num+categoria+persona"` se
  ponía con solo chequear que *alguna* persona con ese nombre existiera en el
  catálogo (`per_id is not None`) — sin verificar que esa persona fuera la dueña
  del objeto elegido. Resultado: quedaban premios vinculados al objeto de otra
  persona, con una etiqueta que decía "confirmado por persona" sin haberlo estado.
  Encontrados así: filas 60 (Argenia R. de Lautafy → objeto de Rosalía Gutiérrez),
  61 (Corina Aguirre → objeto de Consuelo Freixá), 99 (Dominga Nieva → objeto de
  Isabel Ovejero, "colcha" del fallo vs "dos corbatas" del objeto).
  Corregido: la etiqueta ahora solo dice "+persona" si el filtro de persona
  realmente se aplicó a algún número del premio.
- **Casos parecidos pero no necesariamente errores:** filas 58 (Mamerta Monteros
  / "Mamerta Monteros -Escuela Sarmiento") y 79 (hermanas dominicas / "Hermanas
  dominicas- asilo") — probablemente la misma persona/institución con el nombre
  completado en el catálogo; no fusionadas, no confirmado.
  Fila 62 (Mercedes Pereyra / María M. Pereira) ya la había revisado Larisa en
  su comentario ("Coment LM"): confirma que es la misma persona, falta unificar
  el nombre.
- **`premios_manual.csv` ahora acepta `objeto_id = "ninguno"`** para forzar que
  un premio quede sin objeto (sin correr el cruce automático), en vez de solo
  poder forzar un `objeto_id` puntual.

## 2026-09-15 — Limpieza del repositorio y parámetros del pipeline

- **Parámetro único del pipeline: `UMBRAL = 87`** en `03_candidatos.py` — el ratio
  mínimo (0–100) de `rapidfuzz` por debajo del cual un par de nombres no se propone
  como candidato a duplicado. Con 87 salen 75 pares detectados. Bajarlo aumenta el trabajo de
  revisión manual y los falsos positivos; subirlo deja pasar variantes con partícula
  ("Rosa V. de Lezcano" / "Rosa V. Lescano"), que es justo el caso que más aparece.
  No hay modelos entrenados ni semillas de aleatoriedad: queda registrado acá por el
  art. 19 de los *Lineamientos UNSAM* ("registro de modelos, versiones y parámetros").
- **Las 42 fusiones de expositoras salieron del código a una tabla de decisión**
  (`data/interim/decisiones/fusiones_expositoras.csv`). Estaban hardcodeadas en tres
  listas Python dentro de `04_aplicar_dedup.py`; ahora el script solo ejecuta y la
  decisión es un dato revisable sin abrir código, igual que el resto de
  `data/interim/decisiones/`. La columna `origen` conserva de dónde salió cada una.
- **La línea de base de `audit_comentarios.py` pasó de `tests/golden/` a
  `tabla_normalizada_manual.xlsx`.** El golden se re-congela junto con las salidas, así
  que la auditoría se comparaba contra una foto de sí misma y daba siempre "idéntica".
  La base correcta es la tabla tal como la dejó la investigadora, antes de que el
  pipeline aplicara nada. Con el cambio, el informe reporta 83 objetos reasignados y
  48 filas de `Expositoras` eliminadas.
- **El encabezado del informe de auditoría ahora se calcula.** Estaba escrito a mano
  dentro del generador y afirmaba que ninguna fusión se había aplicado, mientras las
  filas del mismo informe listaban 45 `FUSIÓN OK`.
- **`premios_vinculados_v2.xlsx` pasó a ser `premios_vinculados.xlsx`.** Versionar a
  mano dentro de un repo git deja al que clona viendo la salida vieja.


## 2026-09-15 — El pipeline vuelve a ser acíclico (y reproducible)

- **`03_candidatos.py` leía la salida de dos etapas posteriores.** Leía
  `data/processed/tabla_normalizada.xlsx`, que escriben `04b` y `04c`, así que en cada
  corrida la etapa 03 partía de la salida de la corrida anterior. Consecuencia medida:
  con la tabla sin deduplicar, 519 expositoras → **75 pares**; una vez aplicadas las
  fusiones, 471 expositoras → **22 pares**. El 12 de septiembre el archivo anotable se
  reescribió de 77 filas a 22. Los pares no estaban "mal": esas duplicadas ya no
  existían. Pero el pipeline dejaba de ser reproducible desde el crudo.
- **Arreglo:** `03_candidatos` lee ahora `data/interim/tabla_normalizada_manual.xlsx`,
  la misma línea de base fija que usan `04_aplicar_dedup` y `audit_comentarios`.
  Ninguna etapa lee la salida de una posterior. Verificado: tres corridas seguidas dan
  un archivo idéntico.
- **`03_candidatos` dejó de destruir anotaciones.** Relee su propia salida y conserva
  `Hecho`/`Comentarios` por `(id_A, id_B)`; los pares ya listados se mantienen aunque
  la detección no los proponga (columna `detectado`), y `ya_fusionada` marca los que el
  CSV de fusiones ya resolvió. Esta era la regla declarada en esta misma bitácora el
  2026-09 ("nunca se pisan anotaciones") y que el código no cumplía.
- **Dos bugs encontrados al escribir la prueba:** las celdas vacías de Excel llegaban
  como `NaN` y se escribían como el texto literal `"nan"`; y `main()` resolvía las rutas
  al importar el módulo en vez de al correrlo.

## 2026-09-18 — Auditoría de la documentación contra los datos

Se corrió el pipeline entero y se verificó, dato por dato, lo que afirmaban el README,
`src/pipeline/README.md`, el diccionario y `docs/tareas_pendientes.md`. Resultados:

- **El pipeline es reproducible.** Corriendo `python run_pipeline.py` sobre el repo
  limpio, las cinco salidas quedan idénticas celda por celda a las commiteadas. La
  única diferencia es la metadata del zip de cada `.xlsx`, que hace que `git status`
  las marque como modificadas igual.
- **Tres tareas de `tareas_pendientes.md` ya estaban hechas** y el documento no lo
  reflejaba: los 6 `expositora_id` mal asignados (ya corregidos en
  `tabla_normalizada_manual.xlsx`, con lo cual Ramona S. de Varela y Angélica Aguirre
  dejaron de estar huérfanas), la desincronización de la vista plana en los tapices de
  1916, y `outputs/` vacío (hoy tiene `mapa_procedencias.html`). Otras tres estaban
  desactualizadas en los números (género: 8 M y no 5; nombres con espacio final: 7 y
  no ~10; premios: `persona_id` ya está puesto).
- **`03b_premios.py` sigue leyendo la salida de una etapa posterior**
  (`data/processed/tabla_normalizada.xlsx`, que escriben `04b`/`04c`/`04d`). Es el
  mismo ciclo que se cerró en `03_candidatos` el 2026-09-15 y que quedó sin cerrar
  acá. `src/pipeline/README.md` afirmaba que ninguna etapa leía la salida de una
  posterior: era falso y se corrigió.
- **`tests/golden/` quedó desactualizado y `06_verificar` falla siempre**, porque el
  snapshot no se re-congeló después de que `04d` agregara `lat`/`lon` y `04c`
  agregara `Imagen`. Mientras tanto la etapa 06 no verifica nada. Re-congelarlo va en
  un commit propio, según la regla de `tests/golden/README.md`.
- **Dos fusiones del CSV contradicen el comentario anotado a mano**, las dos con
  `origen = sin_lado`: `4,404` (Dalmira González Sorol — el comentario pedía dejarlas
  separadas) y `222,115` (María Ávila — pedía conservar 115 y quedó 222). El criterio
  automático "conservar el lado con más objetos" pisó una decisión humana; hay que
  revisarlas a mano. *María Ávila quedó resuelta el mismo día: la fila pasó a
  `115,222` y la auditoría da `FUSIÓN OK`. Queda pendiente Dalmira.*

## 2026-10-12 — Números de orden corregidos contra el escaneo

El premio de Lastenia Barrero cita "pañuelo n.º 19" y los pañuelos de 1915 llegaban
sólo hasta el 18. Mirando la foto (DSCN5177) el catálogo imprime **16, 19, 18**: no hay
17, y al transcribir se había renumerado en secuencia. Con eso se comparó, para cada
categoría, el rango de `Paginas_Catalogo` (`orden_desde`–`orden_hasta`) contra los
números transcriptos, y se buscaron números repetidos. Cada caso se resolvió en la foto
y se corrigió a mano en `tabla_normalizada_manual.xlsx`:

| objeto | expositora | `ORDEN` | foto | qué pasaba |
|--:|---|---|---|---|
| 17 | Lastenia Barrero | 17 → 19 | DSCN5177 | el catálogo salta del 16 al 19; el premio n.º 19 ahora se vincula solo |
| 352 | Elena Segura | 108 → 109 | DSCN5210 | dos "sobrecama bordada" con el mismo 108 |
| 651 | María E. Pereyra | 28 → 58 | DSCN5218 | transcripto como 28 (que ya era de Arsenia Fernández) |

Quedan dos huecos que **no son errores de la tabla**:

- **Pañuelos 1915, n.º 17** y **Bordado en blanco y seda 1915, n.º 9**: no existen en
  el catálogo impreso (DSCN5177, DSCN5184). El control los va a seguir mostrando.
- **Tapices 1916, n.º 16–25**: `Paginas_Catalogo` decía 1–25 para DSCN5202, pero en las
  fotos sólo hay hasta el 15, igual que en la transcripción. Se corrigió `orden_hasta`
  a 15. Puede ser un error al cargar el índice o una página del catálogo que nunca se
  fotografió: si aparece el original, revisar.

## 2026-10-12 — `UMBRAL` de `03_candidatos` baja de 87 a 80

Con 87 el detector no veía pares como "Argenia R. de Lautafy" / "Arsenia R. de Lontayf"
(80) ni "Hermanas dominicas- asilo" / "Hermanas Dominicas" (85,7). Se midió sobre la
tabla de partida cuántos pares nuevos saldría revisar con cada valor:

| `UMBRAL` | pares detectados | nuevos respecto del archivo de candidatos |
|---|---|---|
| 87 | 85 | 0 |
| 80 | 135 | 48 |
| 75 | 343 | 256 |
| 70 | 689 | 602 |

Con 70 casi todos los nuevos son ruido: mismo apellido y otro nombre de pila (Lola /
Pabla González, Asunción / Visitación Díaz). Se eligió 80 (decisión de Julián). Los
pares ya anotados se conservan con sus comentarios, como siempre. Los demás umbrales
del pipeline están en la tabla de parámetros de `src/pipeline/README.md`.

## 2026-10-12 — Ciudades: revisión LM 9-10 y punto de provincia

- **`coordenadas_ciudades.csv` pasa a ser la única fuente de la ubicación de cada
  ciudad.** `04d_coordenadas` toma de ahí también `nombre_ciudad_hoy` y
  `nombre_provincia` (antes salían de la tabla manual, que tenía su propia copia y
  llegó a diferir: "Villa Vitulumba" / "Villa Tulumba"). Se agregan las columnas
  `lat_provincia`, `lon_provincia`, `precision` y `nota`. Los valores anteriores quedan
  en el historial de git; cada cambio de la revisión lleva nota "LM 9-10: …".
- **Punto de provincia:** la capital de cada provincia, para que en el mapa aparezca
  también lo que sólo tiene provincia (pedido de LM). San Miguel de Tucumán y
  Resistencia son las coordenadas que dio LM; las demás se cargaron a mano y Julián
  las verificó. Sin punto de provincia quedan las provincias dudosas o vacías.
- **Cambios de LM aplicados:** coordenadas corregidas o cargadas para Ingenio
  Trinidad, El Tobar, San Antonio de Quisca, Las Lechuzas, Ingenio Luján, Asilo Ciudad
  (26 y 79, centro de San Miguel) y Leales (Villa de Leales, `precision = tentativa`);
  nota para Ingenio Guzmán; Orán, Concordia y La Banda quedan con provincia sin
  definir y Orán también sin punto (puede ser el de Tucumán o el de Salta).
- **No se aplicaron:** Chicligasta (la coordenada de LM lo llevaba 67 km al oeste, a
  la zona de montaña; se deja la nuestra) y la normalización de "F.C.N.O.A." en
  Arcadia (se deja como está).
- **Vista plana:** se agregan Provincia, "Lugar en el documento" (el texto del
  catálogo), `ciudad_id` y el punto de provincia, para que LM pueda ver de dónde sale
  cada ubicación.

## 2026-10-13 — El mapa pasa al pipeline (`05b_mapa`)

`outputs/mapa_procedencias.html` lo exportaba a mano `notebooks/04_eda.ipynb`, y como
nadie lo volvió a correr quedó con datos viejos ("Villa Vitulumba", Orán con punto, sin
las coordenadas de la revisión LM 9-10). Ahora lo genera la etapa `05b_mapa` en cada
corrida, a partir de la tabla normalizada. Agrega una capa "sólo provincia": lo que no
tiene punto de ciudad se suma en la capital de su provincia, con otro color (pedido de
LM). Las ubicaciones tentativas van con borde punteado. El notebook muestra el mismo
mapa (importa la etapa) y ya no escribe el archivo, para que no pise la versión del
pipeline.

## 2026-10-18 a 22 — Explorador web (`05c_explorador`)

- **El explorador es una etapa del pipeline.** `outputs/explorador.html` se genera desde
  la tabla normalizada con la plantilla de `src/pipeline/plantillas/`: un único archivo,
  sin servidor, que se abre en el navegador.
- **Mapa base: Esri World Street Map**, como en `05b_mapa`. `tile.openstreetmap.org`
  bloquea las páginas abiertas como archivo local, que es como se va a compartir.
- **Zonas** (`decisiones/zonas_ciudades.csv`): cada `ciudad_id` va a una zona (capital
  y alrededores, centro y sur, valles y norte de Tucumán, otras provincias). La
  propuesta inicial salió de la provincia y la distancia a la capital (columna
  `criterio`) y se corrige a mano. A validar con LM.
- **Familias** (`decisiones/familias_categorias.csv`): cada categoría del catálogo va a
  un tipo de obra y tiene una técnica por defecto para cuando el texto del objeto no
  nombra ninguna. A validar con LM.
- **Técnicas:** se infieren del texto del objeto con reglas fijas del script
  (`REGLAS_TECNICA`). No están validadas; el 25/10 se armó
  `decisiones/tecnicas_materiales.csv` para que LM las revise y reemplacen a esas reglas.

## 2026-10-25 — Revisión de LM: pares, premios y Santiago

- **Todo entra por tablas de decisión** (pedido de Julián): nada se corrigió a mano en
  la tabla manual. Dos tablas nuevas que lee `04_aplicar_dedup`:
  `nombres_expositoras.csv` (nombre final después de fusionar; hasta ahora los nombres
  con corchetes se escribían a mano en la tabla) y `fusiones_ciudades.csv`.
- **Expositoras:** 6 fusiones nuevas según las respuestas de LM en
  `pares_sin_revisar.xlsx` y en la hoja Premios (Facunda Cerone [Coronel]). 464 → 458.
- **Premios:** Marina Belmonte y Dalmira quedan fuera de catálogo; Facunda se cierra
  con el objeto 93. La blusa de las Dominicas **no** se vinculó al objeto 149 como
  sugería LM, porque ese objeto ya tiene su propio premio (fila 79): queda pendiente,
  como el de Dominga Castaño.
- **Santiago (50) se une a Santiago del Estero (5).** El 13/10 se había hecho y
  deshecho a la espera de la respuesta de LM; ahora ella lo confirmó.
- **Álbum de 1915:** la transcripción de LM queda en `decisiones/album_1915.csv`. Ya
  sirvió para la blusa (n.º 4 "traje bordado Richelieu", DSCN5159).

## 2026-10-25 — Premios: una sola hoja, ya cruzada con el catálogo (`04e_premios`)

Los vínculos premio–obra estaban en dos lugares que no coincidían: la hoja `Premios` de
la tabla procesada (la de la tabla manual, con 43 filas marcadas "revisar" y vínculos
viejos) y `premios_vinculados.xlsx`, que armaba `03b` y sólo leía el explorador. La
auditoría y el EDA leían la hoja vieja.

- `03b_premios` pasa a ser `04e_premios` y corre después de `04d`, sobre las
  expositoras, objetos e imágenes de la misma corrida: se cierra el último ciclo del
  pipeline.
- Escribe la hoja `Premios` curada en `tabla_normalizada.xlsx` (pedido de Julián: "la
  hoja premios debería darme todos los premios con el catálogo ya cruzado y curado").
  Una fila por premio, con lo que dice el fallo, la obra del catálogo, `Estado`,
  `Vínculo` y `Nota`. Las columnas de trabajo de la revisión no van.
- `premios_vinculados.xlsx` se elimina. El explorador, la auditoría y el EDA leen la
  hoja nueva; la auditoría toma los comentarios de la hoja original y el vínculo de la
  curada.
- **Explorador:** un premio que abarca varias obras (Rosa Alderete, randas n.º 17–21;
  Palmira Contreras, 4 y 5) se contaba una vez por obra y la ficha decía "5 premios".
  Ahora cada premio lleva su `premio_id` y se cuenta una vez.

## 2026-10-25 — Arreglos chicos y tabla de técnicas y materiales

- Nombres actuales de ciudades con tilde o errata corregidos en
  `coordenadas_ciudades.csv`: Famaillá (era "Faimalla"), Concepción (35 y 59), Río
  Chico, Banda del Río Salí (12 y 75: son dos ingenios distintos de la misma
  localidad, no se fusionan).
- Créditos del explorador: estudiante (Julián Rolando), dirección (Larisa Mantovani) y
  tutoría (Agustín Moro); el programa es la optativa del Proyecto Interdisciplinario
  CIAI-LCD, no una "pasantía de investigación" (Recomendaciones, §7).
- `decisiones/tecnicas_materiales.csv`: cada término de técnica, proceso o material que
  aparece en los textos de las obras, con un patrón de búsqueda, una propuesta de
  nombre, cuántas obras lo mencionan, un ejemplo y si el explorador lo reconoce hoy.
  La columna `validacion_LM` queda para que la complete LM. Todavía no la lee ninguna
  etapa: cuando esté validada reemplaza a `REGLAS_TECNICA` de `05c`.

## 2026-10-25 — Chaco en dos localidades, Antofagasta y limpieza

- **Chaco (53) se separa** (`separaciones_ciudades.csv`, mecanismo nuevo en
  `04_aplicar_dedup`): las 2 frazadas de la India de la Misión Franciscana de Nueva
  Pompeya pasan a la ciudad 82, con la coordenada que dio LM (−24,93; −61,48); el
  jergón de Amelia Zunubate queda en 53, con Resistencia como punto de provincia. Antes
  no se podía aplicar la coordenada de LM porque un `ciudad_id` tiene un solo punto.
- **Antofagasta (16)** se ubica en Antofagasta de la Sierra, hoy Catamarca, para el
  mapa (decisión de Julián). El catálogo dice "Antofagasta Salta" y el fallo
  "Catamarca"; en 1915 era el Territorio Nacional de Los Andes. Coordenada verificada por
  Julián (−26,06; −67,41).
- **Se borra lo obsoleto y sin uso** (criterio de Julián): `02_entidades.py` con
  `personas_prov.csv` y `ciudades_prov.csv`, y `revision_duplicados_regenerado.xlsx`.
- **Categorías:** Chales de vicuña / Chales y echarpes y los Jergones siguen separados,
  como se había decidido, aunque la numeración del catálogo continúe de una a otra.
- **Orán:** no se decide nada; la nota de El Orden queda como pregunta para LM.

## 2026-10-25 — "Fuera de concurso" y "creación de la autora" como dato aparte

El catálogo de 1916 marca 2 obras "(fuera de concurso)": se exhibieron pero no
compitieron. Y 12 obras dicen "creación de la autora" (diseño propio). Hasta ahora sólo
estaba en el texto. La etapa nueva `04f_marcas_objetos` lo lee y lo deja en dos columnas
de `Objetos` (`fuera_de_concurso`, `creacion_autora`), que también salen en la vista
plana; el texto del catálogo queda igual (decisión de Julián: no perder información).
"India de la Misión Franciscana de Nueva Pompeya" queda tal como la nombra el catálogo,
sin nota.

## 2026-10-25 — Fotos del álbum de 1915 vinculadas a sus obras

LM transcribió qué pieza se ve en cada foto del álbum de 1915 (n.º, descripción,
posición). Nos tocaba encontrar cada pieza en el catálogo: se cruzó por n.º y
descripción, y se revisó a mano. 12 de las 14 quedan vinculadas (`objeto_id` en
`decisiones/album_1915.csv`). Una primera prueba automática daba sólo 10: comparaba
palabras sueltas y elegía mal la sobrecama de filet (es Encajes varios n.º 8, D'Empaire)
y el "22 Pañuelo" (Encajes varios n.º 22, "dos pañuelos guipure al bolillo"). Quedan
para LM el poncho sin número y el "17 encaje ñanduty". `04c` agrega
`Objetos.foto_album`, que sale en la vista plana y en la ficha del explorador.

## 2026-10-25 — Auditoría completa del repositorio y correcciones

Se leyó cada archivo versionado (docs, código, tablas de decisión, cada hoja de cada
Excel) y se corrió el pipeline en una copia limpia: las salidas se reproducen celda por
celda. Correcciones aplicadas (decisión de Julián, punto por punto):

- **`objetos_texto_override.csv` reintroducía dos errores.** Fijaba el N.º de orden de los
  objetos 352 y 651 en 108 y 28, los valores equivocados que se habían corregido contra el
  escaneo el 2026-10-12; el crudo ya dice 109 y 58. Se borraron esas dos filas y se agregó
  la del objeto 17 (17 → 19, DSCN5177), así `objetos_crudos.csv` coincide con la tabla.
- **Asilo Maternal Ciudad (11)** pasa a San Miguel de Tucumán, como Asilo Ciudad (26 y
  79): las 3 obras de las Hermanas de la Inmaculada Concepción quedan ubicadas.
- **`Paginas_Catalogo`:** DSCN5226 cubre 27–54 (pág. 52) y 55–79 (pág. 53), antes se
  pisaban en 54–55; la nota de DSCN5220 dice "Igual que DSCN5219.JPG". Que falte
  DSCN5209 está bien.
- **Espacios de más:** `limpiar_texto` (`_util.py`) los saca en `01` y, para todas las
  hojas de la tabla manual, al entrar en `04` (21 objetos, 8 nombres, 7 celdas de Premios,
  1 de Paginas_Catalogo). `04b` ya no hace su propio `strip`.
- **Notas de `fusiones_expositoras.csv`** que citaban mal el comentario (9 filas, p. ej.
  `76,67` decía "dejamos A" y se conservó B): ahora citan el texto real.
- **Coordenadas sin normalizar:** provincias "tucuman o cordoba" y "S/d" quedan vacías con
  nota; nombres actuales "Simoca ?", "Santa Rosa o Villa de Leales", "DELFIN GALLO o Ex
  Ingenio Luján", "Los Perez" se normalizan; 26, 41, 45 y 79 reciben nombre actual; se
  borra la fila muerta 50 (fusionada en 5).
- **Nombres** (`nombres_expositoras.csv`): tildes según el pedido de LM (Catalán, Suárez,
  Vázquez, Ordóñez…), "de" en minúscula, abreviaturas "Sra." y "Sta.". "Marcedes Cayata"
  queda así: el catálogo lo imprime así (DSCN5212). Julián confirma que Ataliva Salazar
  (185) es varón y que "Vidal Victoria" (520) es Victoria Vidal: el CSV suma la columna
  `genero` para corregir el de la tabla manual (quedan 449 F y 9 M).
- **Pares candidatos:** en `duplicados_expositoras_candidatos.xlsx`, los pares de Delina
  161/255 y 209/264 pasan de `Hecho = True` a `False` (el comentario siempre dijo
  "separadas"); se cargan como `False` las respuestas de LM del 25/10 para 227/315 y
  93/360. Los 30 pares nunca revisados no se mandan: Julián los da por personas
  distintas. Quedan 50 "sin revisar" en `03_candidatos`.
- **Premio de Dominga Castaño (`premio_id` 6):** pasa de pendiente a fuera de catálogo
  (Julián: no es Dominga Lescano). Quedan 89 vinculados, 12 fuera de catálogo y 1
  pendiente (la blusa de las Hermanas Dominicas).
- **Prensa y archivo:** se repasaron fila por fila las hojas "no PRENSA-EL ORDEN", "no
  ARCHIVO PADILLA" y "no Prensa-Rakow lib" (`docs/relevamiento_prensa_archivo.md`). En
  la tabla manual, `Fuentes` completa la fila 4 (El Orden) y suma el Archivo Padilla
  (5) y la nota de Páez de la Torre (6); `Concursos` suma fechas, sede y organización
  de cada concurso. Nueva `decisiones/menciones_prensa.csv`: 14 menciones de obras,
  expositoras y lugares. Hallazgos: las 7 obras de Mercedes Pacheco son del Colegio de
  la Sagrada Familia, que ella dirigía; Isabel Bascary de Acuña Zavalía era de la
  comisión organizadora y a la vez expositora.
- **Chicligasta:** se confirma nuestra coordenada (no la de LM 9-10); queda la nota en
  `coordenadas_ciudades.csv`.
- **Ingenio Concepción (12) e Ingenio Guzmán (75):** según LM 9-10 son el mismo ingenio.
  Julián decide no unirlos: quedan como los escribió el catálogo; los dos tienen
  Banda del Río Salí como localidad actual y el mapa ya los muestra en un solo punto.
- **Premios:** las notas citan `premio_id`, no la fila de Excel; `premios_manual.csv`
  documenta `pendiente`. El explorador separa los 2 premios pendientes de los 11 fuera de
  catálogo.
- **Mapas:** un círculo por localidad actual en `05b` y en el explorador (antes Cafayate,
  Concepción, Banda del Río Salí y Medinas salían duplicados); el borde punteado significa
  "sólo provincia" en los dos; `05b` da el mismo HTML en cada corrida.
- **Explorador:** `<!doctype>` y `<meta charset>`; título del formulario ("Cartografías del
  textil argentino"); "Proyecto Interdisciplinario"; ya no afirma que el Nivel 1 esté
  cerrado.
  Sin modo oscuro: se ve siempre claro, aunque el sistema esté en oscuro (Julián).
- **Pipeline:** `run_pipeline.py 04d` arranca en 04d; `06` deja de comparar
  `revision_duplicados.xlsx` (insumo, no salida); una sola regla de institución
  (`INSTITUCION`, `_util.py`) para el explorador y el EDA.
- **Docs:** números al día (61/77 ciudades con punto, 449 F y 9 M, 141 pares candidatos,
  estado real del golden) y lo que quedó abierto, en `tareas_pendientes.md`.

## 2026-10-28 — Respuestas de LM del 28/10

- **Blusa de las Hermanas Dominicas (`premio_id` 67):** queda fuera de catálogo ("no
  tiene número de catálogo, s/d significa sin datos"). Quedan 89 premios vinculados, 13
  fuera de catálogo y ninguno pendiente. Lo de Dominga Castaño (`premio_id` 6) ya estaba
  resuelto así: LM había mirado el objeto de Lescano, no la persona.
- **Instituciones:** LM prefiere una marca propia en lugar de género. Las 8 expositoras que
  reconoce la regla `INSTITUCION` pasan de F a `I` vía `nombres_expositoras.csv` (441 F,
  9 M, 8 I). Mercedes Pacheco sigue como persona, aunque sus obras sean del Colegio de la
  Sagrada Familia.
- **Pares:** no se unen 120/340 (Lastenia Barrero / Barquet) ni 33/410 (Argenia R. de
  Lautafy / Arsenia R. de Lontayf, "podrían ser hermanas"); `Hecho = False` en los
  candidatos. Quedan 48 sin revisar.
- **Registros de dos personas** (6 filas): siguen como registro conjunto, porque son
  envíos colectivos.
- **Álbum de 1915:** el poncho (DSCN5158) queda sin identificar. Lo del ñandutí 17 (¿18 o
  19?) no lo contestó.
- **Orán:** LM se inclina por Tucumán, pero no hay información suficiente; espera la
  respuesta del archivo. No cambia nada en la base.
- `06_verificar` marca 8 celdas de `Expositoras` y 2 de `Premios` contra el golden, todas
  de estas decisiones: hay que volver a congelarlo.

## 2026-10-28 — Obras con sólo la provincia pasan a la localidad de la expositora

Criterio de Julián: si una expositora tiene obras donde el catálogo escribió sólo la
provincia y otras con una localidad de esa misma provincia, las primeras pasan a esa
localidad. Lo aplica `04d` (`localidad_de_la_expositora`); la ciudad del catálogo queda en
`Objetos.ciudad_id_catalogo` y el texto, en "Lugar en el documento". En la ficha del explorador esas
obras llevan la marca "Ubicación deducida" y una nota arriba explica de dónde sale. Si hubiera dos
localidades posibles no se mueve nada y se avisa. Hoy son 53 obras de 7 expositoras:

- Concepción y Rosa Cuello: 33 de "CATAMARCA" a Piedra Blanca (el catálogo pone "PIEDRA
  BLANCA, CATAMARCA" sólo en Alfombras y Tapices de 1916).
- Delia Espinosa: 2 de "TUCUMAN" a Niogasta.
- Escuela Profesional de Mujeres (10), Isabel B. de Acuña de Zavalía (4), Escuela y Hogar
  de Obreras (2), Lastenia Barrero (1) y María Retambay (1): de "TUCUMÁN" a San Miguel de
  Tucumán.

Todos los "TUCUMÁN" a secas están en Alfombras, Tapices, Ponchos y Chales de 1916
(DSCN5201, 5202, 5212, 5213), secciones que escriben "LOCALIDAD, PROVINCIA". Cambia el
criterio del 25/8 (con sólo la provincia, la ciudad queda vacía) para estos casos.

## 2026-10-28 — Controles de calidad (`06b_controles`)

Nueva etapa al final del pipeline: busca en toda la base los errores típicos de
transcribir los catálogos y escribe `outputs/controles_calidad.md`, con id y página de
cada caso. No corrige nada, y lo ya decidido (pares "no se unen", las 6 filas de dos
personas, variantes entre corchetes) no vuelve a aparecer. Primera corrida: sin números
de orden repetidos ni fuera de su página, sin premios cruzados entre personas ni obras
sin página. Casos nuevos: Carmen Pérez (199) en Cerrillos (Salta) y en Atahona (Tucumán);
premios cuyo lugar en el fallo no coincide con el catálogo (17, 35, 73, 93); huecos en
la numeración de 1915 (Bordado en blanco y seda n.º 9, Pañuelos n.º 17).

## 2026-10-28 — Revisión completa antes de presentar

Se cruzó todo contra el crudo y los escaneos transcriptos: integridad entre hojas (sin ids
huérfanos ni duplicados), las 981 obras contra `objetos_crudos.csv` (N.º, sección y
descripción idénticos; las diferencias de nombre son variantes y fusiones decididas), los
102 premios uno por uno contra el fallo (el total, $ 4.440, cierra), las coordenadas
contra su provincia y la documentación (links, rutas, números). Correcciones:

- `Concursos`: la sede de 1915 decía "esquina Sala" (el catálogo: "24 de setiembre y
  salta"); 1916 suma decreto (1/3/1916), sede (Escuela Pedagógica Sarmiento, Rivadavia 40)
  y comisión, que estaban en el catálogo y figuraban s/d.
- Explorador: las fechas de 1915 citan las dos fuentes (el catálogo anuncia 24/9–3/10; El
  Orden, inauguración el 29/9) y 1916 nombra la sede.
- `run_pipeline.py`: `06_verificar` termina con `sys.exit()` y cortaba la corrida; ahora
  se ejecutan todas las etapas y el código de salida se devuelve al final.
- README del pipeline y raíz: números al día (13 fuera de catálogo, 48 pares sin revisar,
  puntos del mapa) y la etapa `06b`; `requirements.txt`: folium no es opcional.
- `notebooks/04_eda.ipynb` vuelto a correr (441 F, 9 M, 8 I).

## 2026-10-28 — Explorador: una sola pestaña de análisis, fuentes y datos descargables

- Panorama, Técnicas por zona y Cuadros pasan a ser una pestaña, **Análisis**, con un
  índice fijo: cifras generales, los dos concursos, procedencia, técnicas, expositoras y
  premios. Cada gráfico tiene su tabla plegada debajo ("Ver tabla"). Los enlaces viejos
  (`#tec`, `view=cua`…) abren Análisis.
- Cada obra de la ficha cita su fuente: "Catálogo de 1916, p. 13 (DSCN5201)", con la
  página impresa de `Paginas_Catalogo` (sección y rango de N.º); los premios sin obra
  citan el fallo. La tabla copiada suma "Nombre en la fuente", "Ubicación" y "Fuente".
- Convención de certeza: lo deducido va subrayado con puntos y explicado al pasar el
  mouse; "Dato deducido" se define en Fuentes y método.
- Botones para descargar la base (una fila por obra) y su diccionario, en CSV con punto y
  coma y UTF-8 para Excel.
- La versión ("versión de trabajo del 28 de octubre de 2026") sale de la fecha de la
  corrida y aparece en la cita y en el pie.
- Al revisar el índice de páginas aparecieron tres bordes de página que no coinciden con
  la transcripción (Pañuelos 1915; Encajes y randas 125/126 y Bordados 54/55 de 1916): van
  a `06b_controles` y a las tareas.

## 2026-10-28 — Explorador: comparación de concursos, prensa, fuentes, sesgo y citas

- Análisis, "Los dos concursos": tabla 1915 / 1916 lado a lado (nombre, decreto,
  inauguración, fallo, sede, presidenta de la comisión, expositoras, obras, lugares,
  premios), desde la hoja `Concursos` y la base sin filtros.
- Prensa de época: `05c` lee `menciones_prensa.csv`. Las 14 menciones de El Orden aparecen
  en la ficha de la persona ("En la prensa de época": cita, diario, fecha y título), como
  "· En la prensa" en la obra y en el panel del lugar en el mapa (Monteros, La Cocha, Orán).
- Fuentes y método suma "Dónde están los documentos" (hoja `Fuentes`; lo no confirmado dice
  "a confirmar") y "Lo que el archivo no dice": expositora no es autora, mujeres sin nombre
  propio, género inferido, obras sin procedencia, premios sin obra, accésits anunciados y
  listados, fallo de 1916 sin relevar. Los números salen de la base.
- "Cómo citar" en APA, Chicago y BibTeX.

## 2026-10-28 — Comisiones, enlace por ficha y procedencia no es origen de la técnica

- Nueva `decisiones/comisiones.csv`: las integrantes de la comisión organizadora y jurado
  de 1915 (catálogo y fallo, más Isabel Bascary de Acuña Zavalía según El Orden) y de 1916
  (catálogo). En Análisis, "Comisión organizadora y jurado" las muestra con su rol en cada
  año. Sólo Bascary de Acuña Zavalía es a la vez expositora; para las demás se indica si
  comparten apellido con alguna expositora (Frías, Colombres, Haurigot, Molina), aclarando
  que no prueba parentesco.
- La ficha muestra su código ("Expositora · n.º 58") y suma "Copiar enlace a esta ficha"
  y "Copiar cita de esta ficha".
- La matriz de técnicas y las Definiciones aclaran que la zona es la procedencia de la
  expositora, no el origen de la técnica; se define "Procedencia".

## 2026-10-28 — Mapa: correcciones de una revisión externa

- El filtro "Obras: Todas" pasa a "Premio: Todas las obras / Solo premiadas".
- "Líneas hacia la sede": al activarlas, la leyenda aclara que unen la procedencia
  declarada con la sede y no documentan un traslado. Las que salen de una ubicación
  aproximada van punteadas. Los lugares con solo la provincia ya no tenían línea.
- Los filtros entran en una sola fila en una laptop de 1366 px (antes, dos filas):
  los desplegables pasan de 15 a 12,5 rem de ancho máximo.
- El contador explica de dónde sale el número: "994 obras" son 981 del catálogo y 13
  premiadas que no figuran en él. En el mapa dice además cuántas se ven (953, o 827 sin
  la capa de provincias) y cuántas no tienen ubicación (41).
- `05b_mapa` (Folium): plurales ("1 objeto · 1 expositora"), el mapa base se llama
  "Mapa base (Esri)" en el control de capas y se puede hacer zoom con los dedos.

## 2026-10-28 — Explorador sin zonas ni tipos de obra

- Las zonas (`zonas_ciudades.csv`) y los tipos de obra (`familia` en
  `familias_categorias.csv`) eran agrupaciones del proyecto, sin respaldo en las fuentes
  ni validadas por LM. Julián decide sacarlas del explorador hasta preguntarle.
- La procedencia se agrupa por provincia, la de la localidad que muestra el mapa: filtro
  "Provincia", gráfico "De dónde venían las obras", columnas de la matriz de técnicas,
  ficha de la expositora y columna del CSV descargable.
- Los premios se agrupan por sección del fallo de 1915, tal como las nombra (19
  secciones, 102 premios).
- Se quitan el filtro "Tipo de obra" y los gráficos "Tipos de obra en 1915 y 1916" y
  "Qué tipo de obra hubo en cada zona". Los CSV quedan en `decisiones/` para la revisión.

## 2026-10-28 — No hay premios de 1916

- El explorador decía que los premios de 1916 "todavía no están cargados" y que el fallo
  de 1916 estaba "sin relevar". No hay premios de 1916: se corrigen esos textos (avisos
  de Premios y del filtro, comparación de concursos, pendientes y "Lo que el archivo no
  dice"). Las cifras de premiadas no cambian.

## 2026-10-28 — Análisis: matriz en tres vistas, filtros visibles y cifras que cierran

A partir de una revisión externa:
- La matriz técnica × provincia se ve en obras, en % de las obras de la provincia o en
  expositoras distintas: Concepción y Rosa Cuello (36 obras) y María Ávila (20) dejan de
  parecer un rasgo de Catamarca. "Sin técnica indicada" va en gris, fuera de la escala
  de color, con una nota de qué secciones caen ahí (colchas, ponchos, alfombras,
  jergones, chales) y cuánto pesan por provincia (Tucumán 30 %, Catamarca 55 %).
- "De dónde venían las obras" se ve en cantidad o en % de cada año, con una nota sobre
  1915 provincial y 1916 interprovincial (en 1915 ya hubo obras de otras provincias).
- Las secciones que no usan algunos filtros lo dicen con una insignia, y el índice
  lateral muestra los filtros activos con "Limpiar filtros".
- Cifras generales explica por qué 994 obras (13 premiadas solo en el fallo), 463
  expositoras (5 solo en el fallo) y 102 premios en 108 obras.
- La nota de la matriz distingue la técnica (inferida por el proyecto) de la categoría
  del catálogo.

## 2026-10-28 — Índice de páginas contra los escaneos

El control "El índice de páginas no coincide con las obras" (`06b`) marcaba tres páginas.
Mirando las fotos, la transcripción estaba bien en las tres:

- **DSCN5177 (Pañuelos 1915):** el catálogo imprime 16, 19, 18, así que la última de la
  página es Ignacia Puparelli (18), como dice el índice. El control comparaba por N.º;
  ahora sigue el orden impreso (`objeto_id`).
- **DSCN5221 (Encajes y randas 1916):** la pág. 42 termina con María de Aguirre (125) y la
  43 empieza con Elena R. de Lemière (126). El índice los tenía invertidos (Lemière
  también aparece en la pág. 42, con el n.º 115).
- **DSCN5226 (Bordados en blanco y deshilados 1916):** la pág. 52 termina con Margarita
  T. Robles (53-54) y la 53 empieza con Ercilia Vera de Cáceres (55). El índice los tenía
  invertidos y con la inicial "R.".

Se corrigieron esas cuatro celdas en la hoja `Paginas_Catalogo` de la tabla manual. Los
rangos de N.º estaban bien. El control da 0.

## 2026-10-28 — Cotejo de la transcripción contra los escaneos

Se compararon las 981 obras con el papel: las 11 páginas del catálogo de 1915
(DSCN5177-5187) y las 21 del de 1916 (DSCN5201-5228), obra por obra (número, expositora,
lugar y descripción). Hasta ahora sólo se había controlado la base contra la
transcripción cruda.

**Errores corregidos** (en `objetos_texto_override.csv` y en la tabla manual; los
nombres en `nombres_expositoras.csv`):

| obra | antes | el catálogo dice | página |
|--:|---|---|---|
| 42 | juego puntilla y entredós | juego de puntilla y entredós | DSCN5178 |
| 88 | carpeta encaje de filet de hilo | Carpeta | DSCN5180 |
| 167 | adorno madramé | adorno macramé | DSCN5185 |
| 227 | Alfombra cudrada | Alfombra cuadrada | DSCN5202 |
| 407 | …bodada con hilo merino | …bordada con hilo merino | DSCN5211 |
| 432 | cubrecma de algodón… | cubrecama de algodón… | DSCN5211 |
| 478 | chaón de vicuña | chalón de vicuña | DSCN5212 |
| 761 | escote de randa | caminos de mesa | DSCN5222 |
| 762 | escote de randa | carpeta randa | DSCN5222 |
| 773-775 | carpetas de randas | carpetas de randa | DSCN5222 |
| 915 | barbero | babero | DSCN5227 |

Nombres: Clemencia **de** Zelarayán → Clemencia Zelarayán (103; catálogo y fallo, sin
"de"), Predeslinda → **Predesfinda** de Lloveras (445), Marta A. Beretta → **Berretta**
(501). Las 762 y 773-775 venían de correcciones viejas del override que estaban mal (762
se había completado copiando la 763).

**Detalles mínimos que no se tocaron** (no cambian el sentido): falta o sobra un "de" en
María C. Arrieta (289, 540), María T. Pérez (335), María R. Morales (490), Amparo
Rodríguez de Aberasturi (726), Josefa M. de Lazarte (125), Elena Gramajo (298), Poncho
vicuña (441), Par alforjas de lana (567, 568), Un par estores (926), Canasta con flores
de lana (515), Randas para alba (749); "un cuello" (740) es "Un cuello al bolillo" por
las comillas de repetición.

**Lo que el papel aclara:** la frazada n.º 93 de Carmen Pérez es de Atahona y el cuello
n.º 101 de "Cerrillos", sin provincia (el "Salta" es del proyecto). Concordia (Josefa
López Rivero) tampoco tiene provincia. La n.º 17 de Crochet 1915 es de "María M.
Pereira", lo que confirma el premio 62. Elvira Rodríguez They no tiene lugar impreso.
Jergones 1916 empieza en el n.º 26 en el propio catálogo; no falta ninguna página.

## 2026-10-28 — Técnicas y materiales con la revisión de LM

LM devolvió `tecnicas_materiales.csv` con un comentario por término (columna
`validacion_LM`). El explorador ya no usa las reglas fijas de `05c` (`REGLAS_TECNICA`):
lee el CSV, que ahora tiene `clave`, `etiqueta`, `grupo` (la técnica general de un
subtipo) y `excepto`. El texto del catálogo no cambia: técnicas y materiales son
etiquetas que se agregan al lado.

Lo que cambia con sus comentarios:
- **Subtipos con nombre propio**, que cuentan también en su técnica general: Encaje de
  bolillos, de aguja y de Venecia, Ñandutí y Frivolité (en Encaje); Bordado Richelieu y
  Bordado en relieve (en Bordado). "Encaje richelieu" va sólo como Bordado Richelieu.
- **Puntilla** deja de ser técnica (es una pieza): la técnica sale del resto del texto o
  de la categoría.
- **Guarda atada** (teñido por reserva, no nudo), **Gobelino (tapiz)**, **Macramé**,
  **Malla / red** y **Esmirna** pasan a ser técnicas; antes esas obras no tenían o
  contaban como otra cosa.
- **Tejido punto de Irlanda** se separa de Crochet, con el nombre que propuso LM.
- "Tejido a mano" no es técnica; "bordado en relieve" no se aplica a las alfombras con
  dibujos en relieve (LM: no se sabe si son bordados).
- **Materiales**, nuevos en el explorador (filtro, ficha y descarga): Lana, Vicuña, Lana
  de llama, Seda, Hilo, Algodón, Hoja de caña, Raffia, Fibra de plátano y Piolín. La
  sección del catálogo también aporta (`material_por_categoria` en
  `familias_categorias.csv`): Chales de vicuña → Vicuña; Raffia imitación con hojas de
  caña → Hoja de caña. "Hilo merino" no cuenta como Hilo.

Cambian 174 obras de las 994; "sin técnica indicada" baja de 318 a 303. Quedan para LM:
Esmirna en alfombras (¿punto de alfombra?), "a bastones" (en "bordada a bastones" o
"frazada a bastones de colores" parece un dibujo a rayas, no una técnica), "pintada a la
aguja" (634, 724: no se toma como encaje de aguja), si Punto de Irlanda va dentro de
Crochet, Bruselas (3 obras, no estaba en la lista), y qué hacer con teñido e hilado.

## 2026-10-28 — Se elimina el golden

Julián decide sacar `tests/golden/` y la etapa `06_verificar`. La base se corrige todo
el tiempo (cotejo, revisiones de LM, nombres de columnas), así que la foto congelada
siempre daba diferencias y había que re-congelarla en cada commit, sin que eso
detectara errores. Los controles que sí sirven siguen en `06b_controles`
(`outputs/controles_calidad.md`) y en `audit_comentarios`. Queda en el historial de git.

En el mismo día: la columna `Imagen` de la vista plana y de la hoja Premios pasa a
llamarse `Imagen del catálogo`, para no confundirla con `Foto del álbum`.

## 2026-10-30 — Categorías normalizadas, como propuesta (`04g_categorias`)

`decisiones/categorias.csv` agrega dos niveles a cada sección sin tocar el nombre que
imprimió cada catálogo: `categoria_norm` (dentro de su catálogo) y
`categoria_comparable` (para comparar 1915 con 1916), con el `criterio` y un `estado`.
La evidencia sale del propio catálogo:

- **Numeración continua.** En 1916, Chales de vicuña numera 1-22 y Chales y echarpes
  sigue en 23-41 (págs. 27-29); Jergones numera 26-36 y se imprime antes que Jergones
  y sobrepelos (1-25, págs. 29-31). Son una serie cada una: 24 secciones → 22.
- **Contenido.** Encajes y randas (1916) no tiene ninguna obra que diga "randa" (50 de
  148 dicen encaje); las randas de 1916 van en Randas (79 de 82). Por eso no se unen, y
  para comparar con 1915 Encajes y randas va con Encajes varios.
- **Equivalencias entre concursos:** Tejidos varios / Tejidos en general; Pellones y
  jergones (1915) / Pellones + Jergones (1916); Deshilado + Bordado en blanco y seda
  (1915) / Bordados en blanco y deshilados (1916). 16 grupos comparables.

Todo queda en `propuesta` hasta que lo revise LM; el explorador no lo usa todavía. Las
dos columnas también van a la vista plana.

*Mismo día, más tarde:* Julián decide sacar `categoria_comparable` ("no me gusta esa
columna"). Se quita del CSV, de la tabla normalizada y de la vista plana; el `criterio`
pasa a explicar sólo `categoria_norm`. Queda `categoria_norm`.

## 2026-10-30 — Redes de participación (`05a_redes`)

Objetivo de la versión anterior del formulario: "reconstruir redes de participación de
artesanas e instituciones" (la versión con ajustes no lo dice así; lo más cercano es la
fila del plan de trabajo "Construcción de relaciones entre expositoras, materiales,
técnicas, lugares de procedencia y exposiciones"). Las fuentes no registran vínculos entre personas, así que la primera
versión usa sólo lo que la base sí dice: quién expuso, desde dónde, en qué concurso y
quiénes organizaron. Sale un grafo (`data/processed/redes.xlsx`, hojas Nodos y Aristas,
para Gephi o networkx) y un informe (`outputs/redes.md`).

- **Datos:** participa (expositora → concurso), procede (→ lugar), organiza (comisión →
  concurso) y es_expositora (Isabel Bascary de Acuña Zavalía, organizadora y
  expositora). 32 expositoras expusieron en los dos concursos, 22 de San Miguel de
  Tucumán.
- **Hipótesis, con `confianza`:** mismo apellido en el mismo lugar (183 pares, 58
  grupos) y apellido en común con la comisión (5). Se marca el tipo de coincidencia;
  "propio = de casada" (62 pares) es el caso que podría ser madre e hija o suegra y
  nuera. La confianza es "baja" si 5 o más registros llevan el apellido (González,
  Pérez, López) y nunca "alta": confirmar un parentesco pide otra fuente. Con la
  comisión sólo se listan los apellidos poco frecuentes; con López o Pérez la
  coincidencia no dice nada.
- **Apellidos** sacados del nombre normalizado: sin corchetes ni tratamientos; en "X de
  Y", Y es el de casada. Las instituciones no entran.

No es un análisis de redes sociales en sentido estricto (no hay relaciones
documentadas entre personas); es la estructura para empezar a buscarlas.

En el explorador (pedido de Julián, mismo día): `05a` corre antes de `05c` y escribe la
hoja `Grupos`; el explorador la muestra en Análisis › Expositoras ("Mismo apellido, mismo
lugar", con la pista marcada débil si el apellido es frecuente) y en cada ficha ("Comparte
el apellido Aguilar en Niogasta con…"). El texto dice siempre que es una pista y que las
fuentes no registran parentescos. En "Fuentes y método", las redes pasan de "Pendiente" a
"En esta versión".

## 2026-10-30 — Pestaña Red en el explorador (sigma.js y graphology)

Julián quiere ver la red en el explorador, no en Gephi. Gephi es un programa de
escritorio y no se puede incrustar, pero lo que hace sí: la pestaña **Red** dibuja el
grafo completo de `redes.xlsx` (528 nodos, 1.098 conexiones) con sigma.js 2.4.0 y
graphology 0.25.4 (+ graphology-library 0.8.0), las bibliotecas que usa Gephi para
publicar redes en la web. Se cargan del CDN con versión fija, como Leaflet.

- **Disposición ForceAtlas2**, el algoritmo de Gephi, 900 iteraciones desde posiciones
  con semilla fija: el dibujo es el mismo en cada apertura. Las aristas a los dos
  concursos pesan 0,03: unidas a todas, aplastaban la red en un disco. Se probaron
  cuatro configuraciones midiendo la distancia media expositora–lugar contra la de dos
  nodos al azar; quedó la de menor proporción (0,27; con linLog daba 0,45).
- **Sin comunidades de Louvain** (Julián, 30/10). Se probaron (33 con 3 nodos o más,
  modularidad 0,85), pero coincidían casi siempre con las localidades: colorear por
  localidad muestra lo mismo sin un algoritmo que explicar ni una semilla de la que
  dependan los grupos. El color "Localidad" usa la de más obras de cada expositora; las
  10 con más expositoras tienen color propio.
- **Controles:** buscador, tipos de nodo, líneas de mismo apellido y misma localidad
  (un solo casillero: separar las de apellidos frecuentes confundía, Julián 30/10; la
  `confianza` sigue en `redes.xlsx`), sólo quienes repitieron, color (concurso, localidad, provincia,
  tipo) y tamaño (obras o conexiones). Al seleccionar un nodo se resaltan sus vecinos y
  el panel lista sus conexiones por tipo, con botón a la ficha.
- El grafo SVG que había en Análisis se sacó: lo reemplaza la pestaña; la tabla de
  grupos queda, con un enlace a la red.

Mismo día, técnicas, materiales y categorías en la pestaña (pedido de Julián):

- **En la red de expositoras**, tres tipos de nodo opcionales (apagados de entrada):
  Técnicas (agrupadas en la técnica general: Encaje, Bordado, Randa…), Materiales y
  Categorías del catálogo, unidos a cada expositora con el número de obras. No entran a
  la disposición, para no mover el dibujo: cada uno va al centro, ponderado por obras, de
  quienes lo usaron. Al seleccionarlo, el panel da las obras por localidad y quiénes. Un
  nodo por obra se descartó: cada obra cuelga de una sola expositora y no agrega
  conexiones. Con muchas técnicas prendidas el centro se llena de líneas; sirven sobre
  todo para seleccionar una y ver quiénes la usaron.
- **Red de lugares y técnicas** (selector arriba del panel): bipartita localidad ↔
  técnica (o material, o categoría), peso = obras, sin personas: 45 lugares, 17 técnicas
  y 125 conexiones. Responde al objetivo del formulario sobre la distribución regional de
  técnicas. Se puede pedir un mínimo de obras por conexión. Quedan afuera las obras sin
  localidad (167: sólo la provincia o sin dato) y sin técnica indicada (260).
- Dato que aparece: de las 112 randas, 37 no tienen localidad: 24 de Orán, 12 de
  Santiago del Estero (sólo provincia), 2 de Santa Rosa y 1 de Catamarca. Orán no tiene
  coordenadas mientras esté pendiente; cuando se ubique (en Tucumán o en Salta) entra
  como nodo, unido a Randa con 24 obras, el segundo después de Monteros (36). La
  provincia elegida sólo cambia su color en la red; sí pesa en el mapa, en la matriz por
  provincia y en el argumento histórico.

**Corrección, mismo día: la red no exige coordenadas.** `05a` y la red de lugares y
técnicas contaban como localidad sólo lo que tenía coordenadas, para dejar afuera "sólo
la provincia" y "S/d". Pero la red no usa coordenadas, y la regla sacaba también lugares
con nombre todavía sin ubicar: Orán (24 obras), Rosario (5), La Banda (3), Santa Rosa,
Villa Nueva, Concordia, Pocitos y Tres Pozos. Ahora es localidad todo lugar con nombre,
salvo "sólo la provincia" y "S/d". Cambian los números de arriba: 535 nodos, 1.133
aristas, 198 pares y 61 grupos por apellido (entran Paz, Alincastro y Quinteros de Orán,
y los Robles unen Monteros con Orán); la red de lugares y técnicas pasa a 52 lugares y
133 conexiones, con 128 obras sin localidad. Orán ya es nodo aunque falte decidir su
provincia; esa decisión sólo cambiará su color y su punto en el mapa.

**También "solo provincia" (Julián, mismo día).** Lo que el catálogo da sólo con la
provincia entra como un lugar propio, "Catamarca (solo provincia)" (59 obras, 27
expositoras), "Santiago del Estero (solo provincia)" (47), etc.: 8 lugares más. No
generan líneas de apellido: dos expositoras de "Catamarca" a secas no son de la misma
localidad, y unirlas sería inventar. Sólo "S/d" queda afuera (2 obras). Quedan 543
nodos y 1.190 aristas; los 198 pares y 61 grupos por apellido no cambian. La red de
lugares y técnicas pasa a 59 lugares y 162 conexiones.

## 2026-10-30 — Revisión contra el formulario, las Recomendaciones y los Lineamientos

Se releyeron los cuatro PDF del proyecto y se cruzaron con el repositorio. El pipeline
corre entero en un clon limpio y las salidas se reproducen celda por celda; los dos
notebooks corren sin errores. Cambios:

- **RENATRA (tarea 4 del formulario):** no se cruza (Julián). La base de tejedores ya no
  está en línea (LM, 28/10). Va explicado en el informe final y en
  `evaluacion_riesgos.md` (ese cruce habría sumado datos de personas vivas).
- **Género en el explorador.** El formulario pide explorar "por género" y el explorador
  no lo usaba. Ahora tiene el filtro Género (Mujeres, Varones, Instituciones; "Sin dato"
  para las 5 obras de quien figura sólo en el fallo), el gráfico "Mujeres, varones e
  instituciones" en Análisis › Expositoras y la columna en el CSV. Sale de
  `Expositoras.Género`; la marca de institución coincide con la regla `INSTITUCION` en
  las 57 obras de instituciones.
- **Técnicas y materiales en la base (`04h_tecnicas_materiales`).** Sólo existían dentro
  del explorador. Las reglas pasan de `05c` a `_tecnicas.py`, que usan `04h` (columnas
  `tecnicas`, `tecnica_origen` y `materiales` en `Objetos` y en la vista plana) y `05c`,
  así la base y el explorador dicen lo mismo. Los datos del explorador no cambian. La
  vista plana suma también `Género`.
- **Objetivo 3 (imágenes):** las tareas lo daban por resuelto con el vínculo
  obra–página escaneada. Lo hecho es eso más 13 de 14 piezas del álbum identificadas a
  mano; la identificación en las fotos queda pendiente.
- **Documentación desactualizada, corregida:** pares sin revisar (48, no 50), las
  imágenes sí están en esta máquina, `outputs/` tiene cuatro salidas, instituciones con
  `I` en la evaluación de riesgos, `menciones_prensa.csv` sí la lee `05c`, semillas de
  la pestaña Red en los parámetros, `redes.xlsx` en el diccionario y la cita de las
  redes de arriba.

## 2026-10-30 — Álbum de 1915: el "17 encaje ñanduty" es Pañuelos n.º 19

La pieza "17 encaje ñanduty" de DSCN5168 queda vinculada al objeto 17, Pañuelos n.º 19
de Lastenia Barrero, "Encaje ñanduty" (confirmado por Julián). La leyenda del álbum copia
ese texto (Encajes varios n.º 18 dice "tapete, encaje ñanduty"); la otra pieza cuadrada
de la foto es Pañuelos n.º 4; y el catálogo imprime los pañuelos 1…16, 19, 18, así que el
n.º 19 es el 17.º de la lista (nuestra transcripción también lo numeraba 17 hasta el
12/10). Quedan 13 de 14 piezas vinculadas; falta el poncho de DSCN5158.

Al revisar las 22 fotos del álbum: las 15 que LM no anotó no esconden piezas sin
identificar. Seis son otras tomas de páginas ya anotadas (5153 y 5154 = 5152; 5155 y
5157 = 5156; 5160 = 5159; 5169 = 5168); 5149 es el sobre, 5150 el Palacio de Gobierno y
5151 un grupo de personas; el resto son vistas generales del salón (5163-5167, 5170),
con piezas sin leyenda.

## Fuentes del crudo que no entran al pipeline

Hojas `no PRENSA-EL ORDEN`, `no ARCHIVO PADILLA`, `no Prensa-Rakow lib`: material de
contexto (prensa de época, archivo Padilla). Se conservan en el crudo y ninguna etapa
las lee. Lo que se tomó de ellas se cargó a mano en `Fuentes`, `Concursos` y
`decisiones/menciones_prensa.csv` (ver `docs/relevamiento_prensa_archivo.md`).
