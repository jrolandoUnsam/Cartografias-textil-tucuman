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

## Fuentes del crudo que NO entran a la base

Hojas `no PRENSA-EL ORDEN`, `no ARCHIVO PADILLA`, `no Prensa-Rakow lib`: material de
contexto (prensa de época, archivo Padilla). Se conservan en el crudo pero no se
procesan.
