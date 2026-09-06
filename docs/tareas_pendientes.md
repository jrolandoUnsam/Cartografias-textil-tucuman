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

- [ ] Aplicar del todo las fusiones `Hecho=True` de `revision_duplicados.xlsx`:
  hoy los objetos ya apuntan al id que sobrevive, pero quedan **33 filas muertas**
  en `Expositoras` (el lado B de cada par). Borrarlas. *(31 de las 33 son el lado
  perdedor de un par `Hecho=True`; las otras 2 se resuelven con la corrección de
  `expositora_id` de arriba.)*
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

- [ ] Unificar `Imágenes/` (raíz) con `data/raw/images/` y registrar la procedencia
  de cada toma.
