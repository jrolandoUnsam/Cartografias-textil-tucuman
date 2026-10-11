# Tareas pendientes

## Preguntas para Larisa

- [ ] **Facunda Cerone (47) / Facunda Coronel (476).** En la revisión de octubre dijo
  no unirlas ("en el catálogo figura como Escuela de la Cocha y La Cocha"). Pero el
  premio de 1915 a "Facunda Coronel, Escuela La Cocha, n.º 23" cae en el deshilado 23
  de 1915, que en el catálogo es de **Facunda Cerone** (objeto 93); la 476 Coronel
  sólo expone en 1916. El propio fallo llama "Coronel" a la Cerone del catálogo, lo
  que apunta a que son la misma persona. Repreguntar antes de cerrar el par.
- [ ] **Dos pares que no respondió:** `325` María Fernández / `334` Arsenia Fernández
  (consecutivas en la misma página, DSCN5217) y `209` / `264` Delina J./I. de Román
  (el resto del grupo Delina está en `Hecho=False`).
- [ ] **Hermanas Dominicas: dos fichas.** `83` "Hermanas dominicas- asilo" (objetos de
  1915) y `499` "Hermanas Dominicas" (1916). Los dos premios de 1915 apuntan a la 499,
  y el de bordado n.º 4 lleva el objeto 149, que es de la 83. ¿Son la misma
  institución? *(en espera, no tocar)*
- [ ] **Posibles duplicados que `03_candidatos` no propuso** (2026-10-11). El detector
  compara el nombre entero con umbral 87 y no ve inicial vs. nombre completo
  ("P." / "Palacios"), texto agregado ("-Escuela Sarmiento") ni erratas repartidas.
  Encontrados con un barrido más laxo y filtrados a mano por ciudad, año y objetos.
  Confirmar en el escaneo antes de fusionar.

  **Muy probable**

  | par | evidencia | escaneos |
  |---|---|---|
  | `162` / `296` Carmen de Moya | nombre idéntico, Colalao del Valle 1916; ponchos, frazadón, vicuña, alforjas / 3 sobrepelos; alforjas n.º 5 y sobrepelos n.º 7‑9 en la misma página. Hoy `Hecho=False`, pero el comentario es la regla genérica del "DE", no una decisión sobre el par | DSCN5205, 5212 / DSCN5214 |
  | `214` Simona Palacios de Castro / `266` Simona P. de Castro | P. = Palacios; Colalao del Valle 1916; mismo tipo de envío (frazadón / ponchos, vicuña, alforjas) | DSCN5210 / DSCN5212‑5215 |
  | `346` Manuela B. de Graña / `472` Manuela Bartolomé de Graña | B. = Bartolomé; San Miguel 1916; encajes al bolillo / bordados | DSCN5218 / DSCN5226 |
  | `33` Argenia R. de Lautafy (1915) / `410` Arsenia R. de Lontayf (1916) | misma inicial R.; las dos con punto de Irlanda (traje / torera); apellido probablemente mal transcripto | DSCN5179 / DSCN5221 |
  | `93` María Elvira Pereira (1915) / `360` María E. Pereyra (1916) | E. = Elvira; San Miguel; crochet / Irlanda. Ojo: `94` María **Mercedes** Pereira es otra | DSCN5185 / DSCN5218 |

  **Probable (misma persona en 1915 y 1916)**

  | par | evidencia | escaneos |
  |---|---|---|
  | `106` Alfonsa de Barceló / `473` Alfonsa Cuadrado de Barceló | San Miguel; raffia 1915 / bordados 1916 | DSCN5186 / DSCN5226 |
  | `108` Mamerta Monteros -Escuela Sarmiento / `485` Mamerta Monteros | San Miguel; raffia 1915 / deshilado 1916. Tiene un premio de 1915: la hoja Premios lo apuntaba a la 485, pero el objeto premiado (200) es de la 108 | DSCN5186 / DSCN5226 |
  | `83` / `499` Hermanas Dominicas | ver el ítem anterior | DSCN5184 / DSCN5227 |

## Errores puntuales en `tabla_normalizada.xlsx` (hoja `Objetos`)
- [ ] **objeto 241**: `Almohadón tela hecha a pala` — se le quitó el punto final,
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

- [ ] **Los 17 pares sin fusionar que sí tienen comentario.** Repasar que el comentario
  siga valiendo y, donde corresponda, bajarlo al CSV de fusiones. El grupo más cargado
  es Delina J./I. de Román (161, 209, 255, 264) y le siguen Carmen de Moya (162 / 296,
  con 7 y 3 objetos) y Segunda Giménez / Jiménez (221 / 268).

  Total del archivo al 2026-09-18 (antes de la revisión de octubre): 85 filas = 58 ya resueltas
  por el CSV de fusiones + 27 sin fusionar (10 sin revisar + 17 con comentario). De
  esas 27, 3 tienen un id que ya no existe en la tabla.

## Género (`Expositoras`)

Hoy son **457 F y 8 M** sobre 465 filas.
- [ ] Criterio para instituciones (hoy marcadas F por convención): decidir si llevan
  género o una marca aparte.

## Categorías

- [ ] Decidir criterio de unificación (sin pisar el nombre original de cada
  concurso; agregar `categoria_norm`):
  - 1916: `RANDAS` vs `ENCAJES Y RANDAS`; `JERGONES` vs `JERGONES Y SOBREPELOS`;
    `CHALES DE VICUÑA` vs `CHALES Y ECHARPES`.
  - entre concursos: `TEJIDOS VARIOS` (1915) / `TEJIDOS EN GENERAL` (1916);
    `PELLONES Y JERGONES` (1915) / `PELLONES` + `JERGONES` (1916);
    `BORDADO EN BLANCO Y SEDA` / `BORDADOS EN BLANCO Y DESHILADOS`.
  - La decisión va a `data/interim/decisiones/categorias.csv`, que todavía no existe.

## Pipeline

- [ ] **`03b_premios.py` lee la salida de una etapa posterior.** Lee
  `data/processed/tabla_normalizada.xlsx`, que escriben `04b`, `04c` y `04d`, así que
  trabaja sobre la tabla de la corrida anterior. Es el mismo ciclo que se arregló en
  `03_candidatos` (bitácora 2026-09-15) y que quedó sin arreglar acá. No rompe nada
  hoy —`premios_vinculados.xlsx` es un callejón sin salida, no lo consume ninguna
  etapa— pero el matching de nombres corre contra nombres ya fusionados y ya pasados
  a título. → apuntarlo a `tabla_normalizada_manual.xlsx`, igual que `03_candidatos`.
- [ ] **`02_entidades` es un esqueleto y nadie consume su salida.**
  `personas_prov.csv` y `ciudades_prov.csv` no los lee ninguna etapa: `01`→`02` están
  desconectadas de `03`→`06`. Decidir entre completarlo (era el camino hacia armar la
  tabla normalizada desde el crudo) o sacarlo de la corrida y dejarlo documentado.
- [ ] **Los `.xlsx` figuran como modificados en cada corrida** aunque el contenido sea
  idéntico: cambia sólo la metadata del zip. Verificado el 2026-09-18: después de
  correr el pipeline entero, las 5 salidas son idénticas celda por celda a las
  commiteadas. Ensucia `git status`; ver si conviene documentarlo y listo.

## Geografía

- [ ] **24 de 77 ciudades siguen sin coordenadas** en
  `decisiones/coordenadas_ciudades.csv` (53 cargadas). Completar las que se puedan y
  fijar un criterio para las ambiguas o desconocidas.
- [ ] `decisiones/ciudades.csv` (`nombre_ciudad_hoy`, `nombre_provincia`) todavía no
  existe como tabla de decisión: esos dos campos hoy viven dentro del Excel manual.

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
- [ ] **`outputs/` tiene una sola salida.** Los objetivos específicos 2 y 3 del
  formulario son visualizaciones/mapas interactivos y vinculación registros↔imágenes.
  El 3 está resuelto (`04c`: 981/981 objetos con imagen). Del 2 hoy sale
  `outputs/mapa_procedencias.html`, que exporta `notebooks/04_eda.ipynb`; las demás
  figuras del EDA (categorías, comparación entre concursos, provincias, expositoras)
  viven sólo dentro del notebook y no se exportan. Falta decidir si se exportan desde
  el notebook o si se agrega una etapa `07_figuras` al pipeline.
