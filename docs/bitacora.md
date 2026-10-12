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

## Fuentes del crudo que NO entran a la base

Hojas `no PRENSA-EL ORDEN`, `no ARCHIVO PADILLA`, `no Prensa-Rakow lib`: material de
contexto (prensa de época, archivo Padilla). Se conservan en el crudo pero no se
procesan.
