# Tareas pendientes

## Normalización de datos

- [ ] **Descripción de objeto con mayúscula inicial.** Que toda la columna `OBJETO`
  (y `Descripción del objeto` en la vista plana) arranque con mayúscula. Hoy es
  inconsistente: la mayoría va en minúscula, algunas en mayúscula (ej. objeto 283).
  → aplicar de forma uniforme en la etapa de normalización.

## Errores puntuales en `tabla_normalizada.xlsx` (hoja `Objetos`)

- [x] **objeto 925**: `102 mantel deshilado y encaje` → `mantel deshilado y encaje`. *(corregido)*
- [x] **objeto 880**: `fundas deshilada` → `fundas deshiladas`. *(corregido)*
- [x] **objeto 844**: `fundas` → `funda`. *(corregido)*
- [ ] **objeto 241**: `Almohadón tela hecha a pala` — se le quitó el punto final,
  pero el 243 (misma expositora, mismo bloque) sí conserva el punto
  (`Colección lanas teñidas … tapices.`). Uniformar criterio de puntuación.
- Nota: objetos 871/872 (CARMEN SAL) están **bien** — el catálogo tenía la errata
  `48, 40` en la celda de orden (por `48, 49`) y en la tabla se corrigió a
  `colcha bordada` (48) / `almohadón` (49).

## Objetos con `expositora_id` mal asignado (erratas de tipeo)

El objeto (texto + orden) es correcto, pero apunta a otra persona:

| objeto_id | catálogo | asignado a (mal) | id actual | id correcto |
|--:|---|---|--:|--:|
| 424, 469, 593 | RAMONA S. DE VARELA | IRENE C. DE AYBAR | 284 | 254 |
| 588 | GABRIEL GONZALEZ | JAVIER CÁRDENAS | 320 | 321 |
| 652 | SOLANA CONSTANTINO | MARIA E. PEREYRA | 360 | 361 |
| 684 | ANGELICA AGUIRRE | JULIA M. CHIROU | 466 | 384 |

- [ ] Corregir esos 6 `expositora_id`. Con eso, RAMONA S. DE VARELA (254) y
  ANGELICA AGUIRRE (384) dejan de estar huérfanas.

## Personas (`Expositoras`)

- [ ] **Quedan 3 filas muertas en `Expositoras`** (sin ningún objeto asociado), las
  tres el lado perdedor de un par `Hecho=True` con comentario "dejamos con tilde" que
  nunca entró al CSV de fusiones. Se cierran agregando 3 filas a
  `decisiones/fusiones_expositoras.csv`:

  | mantener | descartar | nombre |
  |--:|--:|---|
  | 256 | 148 | María Salinas |
  | 301 | 187 | Lugarda Juárez |
  | 345 | 329 | María Slopart de Llavi |

- [ ] **3 pares tienen `Hecho=True` pero un comentario que dice lo contrario.** El
  estado actual de la tabla (separadas) coincide con el comentario, no con la casilla:
  corregir la casilla, no los datos.

  | par | comentario |
  |---|---|
  | 182 / 183 | "estas no son la misma, quizás familia" |
  | 92 / 201 | "estos no son el mismo nombre" |
  | 161 / 255 | "las dejaría separadas de momento" |
- [ ] `Nombre`: hacer `strip()` a toda la columna (~10 nombres tienen espacio final).
- [ ] Revisar los ~20 pares casi-iguales (solo difieren en tilde/punto): decidir
  cuáles son la misma persona y cuáles se dejan separados (`Hecho=False`).

## Género (`Expositoras`)

- [ ] `Eleuterio Gramajo` (1915, PELLONES) figura como **F**. ¿Es varón, o errata de
  "Eleuteria"?
- [ ] Revisar `Jesus Rueda`, `JESUS MEDINA RUIZ`, `VIDAL VICTORIA` (marcados F).
- [ ] Confirmar los 5 marcados **M** (todos de 1916). El reglamento de 1916 dice
  "toda mujer"; Larisa afirma que en 1915 todas eran mujeres.

## Categorías

- [ ] Decidir criterio de unificación (sin pisar el nombre original de cada
  concurso; agregar `categoria_norm`):
  - 1916: `RANDAS` vs `ENCAJES Y RANDAS`; `JERGONES` vs `JERGONES Y SOBREPELOS`;
    `CHALES DE VICUÑA` vs `CHALES Y ECHARPES`.
  - entre concursos: `TEJIDOS VARIOS` (1915) / `TEJIDOS EN GENERAL` (1916);
    `PELLONES Y JERGONES` (1915) / `PELLONES` + `JERGONES` (1916);
    `BORDADO EN BLANCO Y SEDA` / `BORDADOS EN BLANCO Y DESHILADOS`.

## Premios

- [ ] Normalizar la hoja `Premios`: sumar `persona_id`, `concurso_id`, `categoria_id`.
  39 nombres no matchean exacto con `Expositoras` (Delia Ruiz ≈ Delicia Ruiz, etc.).
- [ ] Definir formato de `NÚM` (mezcla enteros, `s/d` y rangos como
  `"17, 18, 19, 20 y 21"`) para poder enlazar con `Objetos`.

## Consistencia entre salidas

- [ ] **`vista_plana_tabla_consolidada.xlsx` quedó desincronizada**: la corrección de
  categoría de los tapices 1916 (objetos 229–243, ahora TAPICES) se hizo en
  `tabla_normalizada.xlsx` pero no en la vista plana (sigue mostrándolos como RANDAS).
  Se resuelve al regenerar la vista con la etapa 05.

## Imágenes

- [x] Unificar `Imágenes/` (raíz) con `data/raw/images/`. *(movidos a
  `data/raw/images/albumes/`; no había duplicados)*
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
- [ ] **`outputs/` está vacío.** Los objetivos específicos 2 y 3 del formulario son
  visualizaciones/mapas interactivos y vinculación registros↔imágenes. El 3 ya está
  encaminado (`04c` asigna imagen a 981/981 objetos); el 2 vive solo dentro de
  `notebooks/04_eda.ipynb` y no exporta nada.
- [ ] **`docs/Hoja de horas.xlsx`** llega hasta el 2026‑08‑17. Es la evidencia de las
  96 horas del cuatrimestre.
