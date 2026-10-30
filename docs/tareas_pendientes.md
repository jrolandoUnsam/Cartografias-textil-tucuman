# Tareas pendientes

## Preguntas para Larisa

- [ ] **Isabel B. de Acuña Zavalía (`persona_id` 58): ¿"B." o "Bascary"?** El catálogo
  (6 veces) y el fallo (2) escriben "Isabel B. de Acuña Zavalía"; El Orden (28/7 y
  30/9/1915) la nombra "Isabel Bascary de Acuña Zavalía", y así figura en
  `decisiones/comisiones.csv`. Opciones: usar el nombre completo de la prensa, marcando
  "Bascary" como dato deducido con su cita, o dejar "B." y aclarar en la ficha "Bascary
  según El Orden". Si se usa la prensa, decidir si el criterio vale para otras
  expositoras que la prensa nombra completas. Aparte, el nombre normalizado dice
  "Acuña **de** Zavalía", que sale de una sola fila del fallo (premio 20); las otras
  siete menciones y El Orden dicen "Acuña Zavalía". Corregirlo en la misma pasada.
- [ ] **Zonas y tipos de obra (28/10).** Los armó el proyecto para el explorador, sin
  respaldo en las fuentes, y se sacaron hasta que LM los revise:
  - *Zonas* (`decisiones/zonas_ciudades.csv`): cada localidad va a una región (capital y
    alrededores, centro y sur, valles y norte de Tucumán, otras provincias) según su
    provincia y su distancia a la capital (columna `criterio`). ¿Sirve una regionalización
    así? ¿Hay una de época o de la bibliografía que convenga usar?
  - *Tipos de obra* (columna `familia` de `decisiones/familias_categorias.csv`): las 24
    secciones de los catálogos agrupadas en tejidos de telar y abrigo, alfombras y
    tapices, encajes/randas/crochet, bordados y deshilados, y otros. Casos dudosos:
    Pañuelos con los encajes, Manteles de té con los bordados, Raffia en "otros".
  Mientras tanto, el explorador agrupa la procedencia por provincia y los premios por
  sección del fallo.
- [x] *(2026-10-25)* **Premio de Dominga Castaño (`premio_id` 6).** Julián: Castaño y
  Lescano son personas distintas; el premio queda fuera de catálogo, como lo anota el
  fallo.
- [x] *(2026-10-28: fuera de catálogo; LM: "no tiene número de catálogo, s/d significa
  sin datos")* **Blusa de las Hermanas Dominicas (`premio_id` 67).** LM
  sugiere el n.º 4 "traje bordado richelieu" (objeto 149; en el álbum, DSCN5159),
  pero ese objeto ya tiene su premio: `premio_id` 79, Bordado en blanco y seda n.º 4, también
  de $25. La blusa es otro premio (Deshilado, sin número).
- [ ] **Orán (73): ¿Tucumán o Salta?** Hoy queda sin punto ni provincia (LM 9-10). Evidencia para la reunión: El Orden, 10/10/1916, "La randa tucumana" (hoja "no PRENSA-EL ORDEN" del crudo): Padilla, de gira por la provincia, visita Orán, "antiguo centro de la randera tucumana"; quien transcribió anotó "no queda claro si se refiere a Salta". En el catálogo hay 24 randas de Orán. No se decide nada sin LM. *LM 2026-10-28: se inclina por Tucumán, pero no hay información suficiente; escribió al archivo de Tucumán que le pasó la nota y espera respuesta.*
- [ ] **Una pieza del álbum de 1915 sin obra en el catálogo** (`album_1915.csv`).
  El "Poncho" (DSCN5158) queda sin identificar (LM 2026-10-28: "es super difícil de
  identificar"). Sigue sin respuesta: "17 encaje ñanduty"
  (DSCN5168): la n.º 17 de Encajes varios es una colcha de filet, y las de ñandutí son
  Encajes varios n.º 18 y Pañuelos n.º 19. ¿El número de la foto es 18 o 19? (no lo
  contestó el 28/10). Cotejo con el escaneo (DSCN5179): la n.º 17 es "Colcha, punto filet"
  de Ignacia Puparelli y la 18 "Tapete, encaje ñanduty" de María R. Coletti.
- [ ] **Prensa y Archivo Padilla (`docs/relevamiento_prensa_archivo.md`):** ¿de qué
  documento salen las fotos del "álbum de 1915"? El Archivo Padilla tiene un boletín del
  concurso interprovincial de julio de 1916 que "tiene las fotos del álbum", y su
  transcripción no está en el crudo. (La presidenta de la comisión de 1915 ya no es duda: el
  fallo firma "Presidenta — Guillermina Leston de Guzmán" (DSCN5258), igual que el
  catálogo y El Orden; el rótulo de la foto del Archivo Padilla, que nombra a Lucila López
  Islas, es el que se equivoca.) ¿Dónde
  está la entrevista a Ana Toledo que cita la hoja de El Orden? ¿Qué es "AHT", en qué
  repositorio está el Archivo Padilla y en qué medio salió la nota de Páez de la Torre?
- [ ] **Pares que no respondió en `pares_sin_revisar.xlsx` (25/10):** *(LM 2026-10-28: no se unen `120` / `340` Barrero / Barquet ni `33` / `410`
  Argenia / Arsenia, "podrían ser hermanas"; cargados como `Hecho = False`. Del resto no
  dijo nada.)* `2` Marina /
  `45` Máxima Belmonte, `390` Audelina y Abigail / `409` María Abigail Gómez, `215`
  Lidia / `474` Lastenia Moya Escobar,
  `366` Manuela / `485` Mamerta Monteros, `129` María Díaz / `176` María Cruz Díaz, `466` Julia M. / `468` Paulina
  P. de Chirou y `435` Rosa / `506` Rita Ariza. También sigue sin respuesta `325` María
  / `334` Arsenia Fernández.
- [x] **Revisión de LM del 25/10** *(aplicada 2026-10-25)*:
  - Fusionadas (`fusiones_expositoras.csv`, nombre en `nombres_expositoras.csv`):
    `83 ← 499` Hermanas dominicas [asilo], `214 ← 266` Simona Palacios de Castro,
    `472 ← 346` Manuela Bartolomé de Graña, `473 ← 106` Alfonsa [Cuadrado] de Barceló,
    `108 ← 485` Mamerta Monteros [Escuela Sarmiento 1915] y `47 ← 476` Facunda Cerone
    [Coronel] (su premio queda en el deshilado 23, objeto 93).
  - No se unen: `227` / `315` Rosario Herrera ("hay MUCHAS Herrera de Chicligasta") y
    `93` / `360` María E. Pereira / Pereyra ("en principio no").
  - Premios fuera de catálogo: Marina Belmonte n.º 22 y el mantel de altar de Dalmira.
  - Ciudades: "Santiago" (50) se une a Santiago del Estero (5)
    (`fusiones_ciudades.csv`).
  - Transcripción de fotos del álbum de 1915: `decisiones/album_1915.csv`. La lee `04c`
    (`Objetos.foto_album`).

## Errores puntuales en `tabla_normalizada.xlsx` (hoja `Objetos`)
- [x] *(2026-10-25: ya ningún objeto termina en punto, ni el 241 ni el 243)* **objeto 241**: `Almohadón tela hecha a pala` — se le quitó el punto final,
  pero el 243 (misma expositora, mismo bloque) sí conserva el punto
  (`Colección lanas teñidas para fabricar alfombras y tapices.`). Uniformar criterio
  de puntuación.

## Personas (`Expositoras`)

- [x] **Las 3 filas muertas de `Expositoras`.** *(2026-09-18, cerrado)* Se agregaron
  al CSV y se corrió `python run_pipeline.py 04`: las tres desaparecieron y sus
  objetos quedaron en el id que sobrevive. Auditoría regenerada: las 3 pasaron de
  `SIN HACER` a `FUSIÓN OK`.

  | mantener | descartar | nombre |
  |--:|--:|---|
  | 256 | 148 | María Salinas |
  | 301 | 187 | Lugarda Juárez |
  | 345 | 329 | María Slopart de Llavi |

- [x] **María Ávila (222/115).** *(2026-09-18, cerrado)* Se corrigió la fila del CSV:
  ahora `mantener=115` (era `222`). Sobrevive 115 con sus 20 objetos, tal como pedía
  el comentario ("dejamos con tilde" → conservar A). Auditoría regenerada: la fila 39
  pasó de `⚠ FUSIÓN REVISAR` a `FUSIÓN OK`.
- [x] **Dalmira González Sorol (4/404).** *(2026-10-11)* La auditoría la marca
  `⚠ CONTRA LO PEDIDO` porque lee "dejaría cada ciudad como está" como "mantener
  separadas". Lectura de Julián: el comentario completo es "Tafi Viejo en 1915 y
  Tucumán 1916 / dejaría cada ciudad como está", o sea que habla de la **ciudad**, no
  de la persona. La fusión ya respeta eso: la ciudad va en cada objeto, y los 6 de
  1915 siguen en Tafí Viejo y el de 1916 en San Miguel de Tucumán. Se mantiene la
  fusión; el veredicto del informe es un falso positivo del parser.
- [x] `Nombre` sin espacios al final. *(2026-10-11)* `04b` hace `strip()` a los
  nombres; los 7 casos (Cipriana González, Carmen V. de Roncedo, Margarita Díaz,
  Ernestina Silvetti, Sra. de Serrano, Carmen Rodríguez, Candelaria Alincastro)
  quedaron limpios.
- [x] **Revisión de Larisa (octubre) de los 10 pares sin revisar.** *(2026-10-11)*
  - Fusionados: `43 ← 479` Sara M. Sal, `344 ← 338` María Llaví de Puig (en la tabla
    figura "Llaví"; la lista que se le pasó decía "Llavé" por error),
    `114 ← 56` Rosa V. [de] Lescano.
  - `Hecho=False` en el archivo de candidatos: 198/303 (Pérez), 170/241 (Zelaya),
    124/171 (Gramajo), 155/334 (Arsenia Fernández).
  - Quedan 3 sin revisar (los cuenta `03_candidatos`): 47/476 Facunda (ver
    *Preguntas para Larisa*), 325/334 María / Arsenia Fernández y 209/264 Delina
    J./I. de Román, que no respondió.

- [x] *(2026-10-25: revisados; hoy son 18 y todos están resueltos — decididos "no unificar" o ya unificados por otro camino, como Ana e Isabel del Río y la Escuela Profesional de Mujeres)* **Los 17 pares sin fusionar que sí tienen comentario.** Repasar que el comentario
  siga valiendo y, donde corresponda, bajarlo al CSV de fusiones. El grupo más cargado
  es Delina J./I. de Román (161, 209, 255, 264) y le siguen Carmen de Moya (162 / 296,
  con 7 y 3 objetos) y Segunda Giménez / Jiménez (221 / 268).

  Total del archivo al 2026-09-18 (antes de la revisión de octubre): 85 filas = 58 ya resueltas
  por el CSV de fusiones + 27 sin fusionar (10 sin revisar + 17 con comentario). De
  esas 27, 3 tienen un id que ya no existe en la tabla.

- [x] *(2026-10-25)* **30 pares candidatos que nunca se revisaron ni se mandaron a LM.**
  Julián: no son la misma persona (mismo apellido y otro nombre de pila, del umbral 80);
  no se mandan y quedan sin anotar a propósito. `03_candidatos` marca 50 pares "sin
  fusionar y sin revisar": esos 30, 12 con un id que ya se fusionó por otro camino y 8
  de `pares_sin_revisar.xlsx` sin respuesta. Las respuestas "no se unen" de LM para
  227/315 y 93/360 se cargaron como `Hecho = False`, y los pares de Delina 161/255 y
  209/264 pasaron de `True` a `False` (el comentario decía "separadas").
- [ ] **Nombres de la auditoría 2026-10-25 para confirmar con LM:** "Sta. Sandés"
  (el "Sta" viene del fallo, probablemente "señorita") y las dos Delina J. / I. de Román con nombres idénticos (161/209, 255/264).

## Género (`Expositoras`)

Hoy son **441 F, 9 M y 8 I** (institución) sobre 458 filas.
- [x] *(2026-10-28)* Criterio para instituciones: LM prefiere una marca propia en lugar de
  género. Las 8 que reconoce la regla `INSTITUCION` llevan `Género = I`
  (`nombres_expositoras.csv`): 37, 50, 83, 102, 281, 364, 398 y 492.
- [x] *(2026-10-28)* **Las 6 filas que son dos personas** (Concepción y Rosa Cuello,
  María Díaz y Victoria Bazán, María Luisa y Angélica Gramajo, Audelina y Abigail Gómez,
  Cristina e Isabel Blay, Virginia Vivolo y Antonia Cerrasuolo): LM, se dejan como registro
  conjunto, porque son envíos colectivos.

## Categorías

- [ ] **Para LM: la propuesta de `decisiones/categorias.csv` (2026-10-30).** La aplica
  `04g`; `nombre_categoria` no se toca. Todo queda en `estado = propuesta`.
  - *Dentro de 1916* (`categoria_norm`), dos uniones por numeración continua: Chales de
    vicuña (1-22) sigue en Chales y echarpes (23-41), y Jergones (26-36) completa
    Jergones y sobrepelos (1-25). ¿Son una sola sección?
  - `RANDAS` y `ENCAJES Y RANDAS` (1916) **no** se unen: las dos numeran desde 1 y
    ninguna de las 148 obras de Encajes y randas dice "randa" (50 dicen encaje), mientras
    que 79 de las 82 de Randas sí.
  - *Entre concursos* (`categoria_comparable`): Tejidos varios = Tejidos en general;
    Encajes varios = Encajes y randas → "Encajes"; Pellones y jergones = Pellones +
    Jergones + Jergones y sobrepelos; Deshilado + Bordado en blanco y seda = Bordados en
    blanco y deshilados → "Bordados y deshilados". ¿Sirve para comparar 1915 con 1916?
  - Mientras tanto, el explorador sigue usando la categoría del catálogo.

## Revisión completa del 28/10 (ver `outputs/controles_calidad.md`)

- [ ] **Carmen Pérez (199):** la frazada n.º 93 dice "Atahona" y el cuello bordado n.º 101
  dice "Cerrillos", sin provincia (DSCN5208 y DSCN5219). Que ese Cerrillos sea el de Salta
  lo decidió el proyecto al cargar coordenadas, no el catálogo. Pregunta para LM: ¿qué
  Cerrillos es? Si es un paraje de Tucumán cerca de Atahona, probablemente es la misma
  mujer. (El informe del 28/10 tenía los dos lugares invertidos.)
- [ ] **Premios cuyo lugar en el fallo no coincide con el catálogo:** Ana Tactagi (93:
  fallo Simoca, catálogo San Miguel), Melchora y Rosa Valenzuela (17 y 35: fallo "Ciudad",
  catálogo Simoca), Elvira Rodríguez (73: fallo San Rafael, catálogo S/D; el fallo
  completaría su procedencia).
- [x] *(2026-10-28: ya verificado el 12/10, no son errores)* **Huecos en la numeración de
  1915:** Bordado en blanco y seda n.º 9 y Pañuelos n.º 17 no existen en el catálogo
  impreso (DSCN5177, DSCN5184). El control los va a seguir mostrando.
- [ ] **Varones:** el decreto del 1/3/1916 abre el concurso a "toda mujer radicada";
  hay 9 expositores varones, 7 de ellos en 1916 (casi todos con pellones) y 2 en 1915
  (Jesús Rueda, colchas; Eleuterio Gramajo, pellones). Confirmar con LM que el
  género está bien y, si es así, es un dato para comentar.
- [x] *(2026-10-28, cotejo DSCN5185)* **Mercedes Pereyra (premio 62)** vinculada a María
  Mercedes Pereira: el catálogo de 1915 dice "María M. Pereira (Ciudad)", Crochet n.º 17,
  y el fallo premia la "No. 17 de Mercedes Pereyra (Ciudad)" en crochet. Confirmado.
- [x] *(2026-10-28, escaneo DSCN5256-5257)* **Accésits de 1915:** el fallo impreso dice
  "Se resuelve crear 9 accesits" y lista 8 (Ovejero, Argentina Sal, Fronzutti, Elvira
  Rodríguez, Mercedes Pacheco, Facunda Coronel, Marina Belmonte y Sara M. Sal). No falta
  ninguno en la transcripción: el error es del propio fallo.
- [x] *(2026-10-28, mirando los escaneos)* **El índice de páginas no coincide con las
  obras.** La transcripción estaba bien en los tres casos:
  - Pañuelos 1915 (DSCN5177): el catálogo imprime 16, 19, 18; Puparelli (18) es la
    última de la página. El control `06b` ahora ordena por el orden impreso
    (`objeto_id`), no por N.º.
  - Encajes y randas 1916 (DSCN5221): la pág. 42 termina con María de Aguirre (125) y la
    43 empieza con Elena R. de Lemière (126). Se corrigió el índice.
  - Bordados en blanco y deshilados 1916 (DSCN5226): la pág. 52 termina con Margarita
    T. Robles (53-54) y la 53 empieza con Ercilia Vera de Cáceres (55). Se corrigió el
    índice, incluida la inicial ("T.", no "R.").

- [x] *(2026-10-28)* **Cotejo de la transcripción contra los escaneos** de los dos
  catálogos (981 obras, 32 páginas). 13 errores corregidos (`objetos_texto_override.csv`,
  tabla manual y `nombres_expositoras.csv`); detalle en la bitácora. Quedan sin tocar unos
  15 detalles mínimos (un "de" de más o de menos) listados ahí.

## Pedidos de LM (28/10)

- [ ] **Darle un lugar donde ver el trabajo.** "Quizás a futuro es mejor pasarnos el link
  de donde trabajamos": le cuesta encontrar dónde está cada cosa (p. ej. las obras con foto
  del álbum). El explorador puede servir de respuesta.
- [x] **Técnicas y materiales:** revisión devuelta y aplicada al explorador (28/10, ver
  bitácora). Quedan para preguntarle: Esmirna en alfombras, "a bastones", "pintada a la
  aguja", si Punto de Irlanda va dentro de Crochet, Bruselas, y teñido e hilado. También
  si se puede asumir una técnica general "(sin precisar)" para las categorías de tejidos
  (Jergones, Pellones, Ponchos, Alforjas, Colchas y frazadas): 138 obras no tienen ni
  técnica ni material en el texto.
- Referencia para el explorador: la Ciapoteca del CIAP (CONICET-UNSAM), hecha en Omeka,
  https://coleccionesciap.ar/s/ciapoteca/page/buenos-aires-de-plata. LM ofrece una
  reunión con el personal técnico del instituto. El modelo que quería (la base de
  tejedores del Renatra) ya no está en línea ni en la Wayback Machine.

## Redes (`05a_redes`, 2026-10-30)

- [ ] **Para LM: qué redes le sirven.** Primera versión con lo que ya está en la base
  (`outputs/redes.md`, `data/processed/redes.xlsx`): 32 expositoras repitieron en 1915
  y 1916; 61 grupos con el mismo apellido en el mismo lugar (los González de
  Chicligasta, los Gramajo de Monteagudo y Niogasta, los Aguilar de Niogasta, los
  Alderete de Monteros); 5 apellidos en común entre la comisión y las expositoras
  (Haurigot, Frías, Colombres, Molina). Las aristas de apellido son hipótesis. Preguntas:
  ¿hay fuentes para confirmar parentescos (prensa, registros)? ¿Interesa la relación
  institución ↔ alumnas (Colegio de la Sagrada Familia, Escuela Sarmiento), que hoy no
  está en los datos?
- [x] *(2026-10-30)* Redes en el explorador: tabla "Mismo apellido, mismo lugar" en
  Análisis › Expositoras y una nota en cada ficha con las otras expositoras del grupo,
  presentadas como pista de parentesco, y la pestaña **Red** con el grafo completo
  (sigma.js, ForceAtlas2), con técnicas, materiales y categorías como nodos opcionales y
  una segunda red de lugares y técnicas. Quienes repitieron y la comisión ya estaban.

## IA sobre fotos (objetivo 6 del formulario)

- [ ] **Faltan las imágenes en esta máquina.** `data/raw/images/` sólo tiene el README;
  para empezar hay que copiar los álbumes de 1915 (`albumes/1915-album-version-2/`,
  DSCN5149–5170) desde el resguardo.
- [ ] Prueba acotada: con un modelo abierto de detección/segmentación, contar las piezas
  de cada foto del álbum y comparar contra `decisiones/album_1915.csv` (piezas
  transcriptas por LM). Registrar modelo, versión y parámetros (Lineamientos, art. 19) y
  reevaluar el riesgo en `evaluacion_riesgos.md`.

## Explorador

- [ ] **Parte premiada en el cúmulo de Tucumán.** El punto rojo (área proporcional a las
  premiadas) se lee bien en los lugares aislados, pero alrededor de San Miguel de Tucumán
  los puntos se superponen y hacen ruido. Probar un anillo parcial en el borde del
  círculo (premiadas sobre total). Sugerencia de una revisión externa, 28/10.

## Pipeline

- [ ] *(2026-10-28: hechos 1 a 4 en `05c`; falta 5)* **Prensa en el explorador y en la vista plana (semana del 26/10/2026).** Una etapa
  lee `decisiones/menciones_prensa.csv` y: (1) en la ficha de cada expositora, un
  recuadro "En la prensa" con la cita, el diario y la fecha; (2) en la lista de obras, la
  marca "· En la prensa"; (3) en los lugares (Orán, Monteros, La Cocha), sus citas; (4) en
  "Fuentes y método", fechas, sede y comisión de cada concurso (hoja `Concursos`), las 6
  fuentes; (5) una
  columna "En la prensa" en la vista plana. Sin hoja nueva en la tabla normalizada.

- [x] *(2026-10-25)* **Re-congelar `tests/golden/`**. *(2026-10-28: el golden y
  `06_verificar` se eliminaron; ver bitácora.)*
- [x] *(2026-10-28)* **Premios 98 y 99 (`decisión a mano`) sin nota.** Notas cargadas en
  `premios_manual.csv`: el portarretrato es la única obra de D'Empaire que coincide con el
  fallo (Varios n.º 3); la colcha de Dominga Nieva es su única obra (Colchas y frazadas
  n.º 4), aunque el fallo impreso dice "No. 9" (DSCN5258), que es de Jesús Rueda.

- [x] **`03b_premios.py` leía la salida de una etapa posterior.** *(2026-10-25)* Ahora
  es `04e_premios`, corre después de `04d` y escribe la hoja `Premios` curada en la
  tabla procesada; `premios_vinculados.xlsx` ya no existe.
- [x] **`02_entidades` era un esqueleto y nadie consumía su salida.** *(2026-10-25)*
  Se borró, con `personas_prov.csv` y `ciudades_prov.csv` (criterio de Julián: lo
  obsoleto y sin uso se borra). Queda en `git log` por si se retoma el armado de la
  tabla normalizada desde el crudo.
- [ ] **Los `.xlsx` figuran como modificados en cada corrida** aunque el contenido sea
  idéntico: cambia sólo la metadata del zip. Verificado el 2026-09-18: después de
  correr el pipeline entero, las 5 salidas son idénticas celda por celda a las
  commiteadas. Ensucia `git status`; ver si conviene documentarlo y listo.

## Geografía

- [ ] **Para LM (auditoría 2026-10-25):** Concordia, La Banda, Rosario, Santa Rosa (72,
  ¿la misma que Leales?), Villa Nueva (¿Tucumán o Córdoba?) y Los Mendoza (¿Simoca?)
  siguen sin ubicar. Chicligasta
  queda con la coordenada nuestra, no la de LM (Julián, 2026-10-25).

- [ ] **16 de 77 ciudades siguen sin coordenadas** en
  `decisiones/coordenadas_ciudades.csv` (61 cargadas). Completar las que se puedan y
  fijar un criterio para las ambiguas o desconocidas.
- [x] *(2026-10-12)* `nombre_ciudad_hoy` y `nombre_provincia` vivían en dos lugares (tabla
  manual y `coordenadas_ciudades.csv`). Ahora el CSV es la única fuente: `04d` los toma
  de ahí. La única diferencia era Tulumba ("Villa Vitulumba" en la tabla).

## Imágenes
- [ ] Decidir cuál de las dos tomas del álbum de 1915 es la de referencia y registrar
  de qué documento físico salió cada foto (hoja `Fuentes`).

## Entregables de la optativa

- [ ] **`docs/uso_de_ia.md`** — qué asistentes de IA se usaron, en qué etapas y cómo se
  verificó su aporte. Lo piden las *Recomendaciones LCD‑CIAI* §6 y el art. 14 de los
  *Lineamientos UNSAM*. Se escribe al cierre, con el proyecto terminado.
- [ ] **Cerrar `docs/evaluacion_riesgos.md` en conjunto con la dirección** y sacarle la
  leyenda "a completar": §10 pide que la evaluación se haga con investigadora y
  estudiante juntos. El contenido y el Nivel 1 ya están.
- [ ] **Acordar con la dirección hasta dónde se publican datos y código** (§7). Es una
  conversación que se registra en el **Anexo V — Autorización de Divulgación** del
  informe final. No requiere ningún archivo en el repositorio.
- [ ] **Publicar el explorador en GitHub Pages** (idea de Julián, 28/10; todavía no).
  Antes: el OK de LM y la licencia (punto anterior), y decidir si el repo pasa a ser
  público o si el sitio va en un repo aparte (en el plan gratuito, Pages exige repo
  público). No usar `docs/` como raíz, porque ahí están la bitácora y la hoja de horas.
  Plan: una carpeta `sitio/` que llene el pipeline, con `index.html` (el explorador),
  `vendor/leaflet/` (Leaflet copiado, sin CDN) y `datos/` (CSV, xlsx normalizado y
  GeoJSON de lugares para descargar). El mapa de Folium no se publica: el explorador
  ya lo cubre.
- [ ] **`outputs/` tiene una sola salida.** Los objetivos específicos 2 y 3 del
  formulario son visualizaciones/mapas interactivos y vinculación registros↔imágenes.
  El 3 está resuelto (`04c`: 981/981 objetos con imagen). Del 2 hoy sale
  `outputs/mapa_procedencias.html`, que genera la etapa `05b_mapa` del pipeline; las demás
  figuras del EDA (categorías, comparación entre concursos, provincias, expositoras)
  viven sólo dentro del notebook y no se exportan. Falta decidir si se exportan desde
  el notebook o si se agrega una etapa `07_figuras` al pipeline.
