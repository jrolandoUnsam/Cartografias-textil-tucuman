# Tareas pendientes

## Preguntas para Larisa

- [ ] **Facunda Cerone (47) / Facunda Coronel (476).** En la revisión de octubre dijo
  no unirlas ("en el catálogo figura como Escuela de la Cocha y La Cocha"). Pero el
  premio de 1915 a "Facunda Coronel, Escuela La Cocha, n.º 23" cae en el deshilado 23
  de 1915, que en el catálogo es de **Facunda Cerone** (objeto 93); la 476 Coronel
  sólo expone en 1916. El propio fallo llama "Coronel" a la Cerone del catálogo, lo
  que apunta a que son la misma persona. Repreguntar antes de cerrar el par.

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
- [ ] **Dalmira González Sorol (4/404) sigue contradiciendo el comentario.** El
  comentario pedía **mantener separadas** ("dejaría cada ciudad como está") y el CSV
  las fusiona (`origen = sin_lado`). Auditoría, fila 68: `⚠ CONTRA LO PEDIDO`. Es la
  única contradicción que queda en el informe.


- [ ] `Nombre`: hacer `strip()` a toda la columna. Son **7** nombres con espacio
  final: Cipriana González, Carmen V. de Roncedo, Margarita Díaz, Ernestina Silvetti,
  Sra. de Serrano, Carmen Rodríguez, Candelaria Alincastro.
- [ ] **Los 10 pares detectados que nunca se revisaron.** Es lo único del archivo de
  candidatos que no tiene ninguna decisión tomada: `Hecho` vacío **y** `Comentarios`
  vacío. El propio `03_candidatos` los cuenta al final de cada corrida
  (`10 sin fusionar y sin revisar  <-- lo que falta mirar`). Los otros 17 pares sin
  fusionar sí tienen comentario: ahí la decisión está tomada (dejarlos separados) o la
  duda está registrada.

  Cada objeto tiene ahora su escaneo (`Objetos.imagen`, que pone `04c`), así que estas
  dudas se resuelven yendo a la foto del catálogo. Agrupados por lo que dice el
  contexto documental:

  **a) Casi seguro la misma persona — confirmar en el escaneo y fusionar**

  | par | por qué | escaneos |
  |---|---|---|
  | `43` Sara M. Sal / `479` Sara Sal | misma ciudad (San Miguel), misma técnica (deshilado) en 1915 y 1916 | DSCN5180 / DSCN5226 |
  | `338` María Ll. de Puig / `344` María Llavé de Puig | `Ll.` es la abreviatura de `Llavé`; misma ciudad, misma categoría, **misma página**, los dos un pañuelo al bolillo | DSCN5218 (órdenes 20 y 33) |
  | `56` Rosa V. de Lezcano / `114` Rosa V. Lescano | | DSCN5181, DSCN5187 / DSCN5201 |

  **b) Casi seguro personas distintas — anotar `Hecho=False` y cerrar**

  | par | por qué | escaneos |
  |---|---|---|
  | `325` María Fernández / `334` Arsenia Fernández | **nombres de pila distintos y figuran consecutivas en la misma página** (órdenes 2 y 11; 68‑69 y 70‑74): el catálogo las lista como dos expositoras, probablemente parientes | DSCN5217, DSCN5226 |
  | `198` María T. de Pérez / `303` María Pérez | apellido muy común, ciudades distintas (Atahona / Ensenada), categorías distintas | DSCN5208 / DSCN5214 |
  | `170` Ofelia Zelaya / `241` Fidelia Zelaya | nombres de pila distintos, ciudades distintas (Niogasta / Chicligasta) | DSCN5205 / DSCN5211 |
  | `124` Adela J. de Gramajo / `171` Adela G. de Gramajo | `J` vs `G`: misma ciudad (Monteagudo) y mismo concurso,  distinta categoría| DSCN5201 / DSCN5205 |
  | `47` Facunda Cerone / `476` Facunda Coronel | ¿errata de transcripción? Misma localidad (Escuela de La Cocha / La Cocha), mismo nombre de pila raro, misma técnica | DSCN5181 / DSCN5226 |
  | `155` Arsenia M. de Fernández / `334` Arsenia Fernández |ciudad y categoría distintas (Chicligasta/frazada vs Concepción‑Medinas/encajes) | DSCN5205 / DSCN5217‑5226 |
  | `209` Delina J. de Román / `264` Delina I. de Román | parte del grupo Delina; 264 no tiene ciudad cargada | DSCN5208 / DSCN5212‑5213 |


- [ ] **Los 17 pares sin fusionar que sí tienen comentario.** Repasar que el comentario
  siga valiendo y, donde corresponda, bajarlo al CSV de fusiones. El grupo más cargado
  es Delina J./I. de Román (161, 209, 255, 264) y le siguen Carmen de Moya (162 / 296,
  con 7 y 3 objetos) y Segunda Gimónez / Jiménez (221 / 268).

  Total del archivo (antes de las 4 fusiones de arriba): 85 filas = 58 ya resueltas
  por el CSV de fusiones + 27 sin fusionar (10 sin revisar + 17 con comentario). De
  esas 27, 3 tienen un id que ya no existe en la tabla.

## Género (`Expositoras`)

Hoy son **460 F y 8 M** sobre 468 filas.
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
