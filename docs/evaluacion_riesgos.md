# Evaluación de riesgos: sesgo y privacidad

Según los *Lineamientos para la gobernanza de datos e IA de la UNSAM* y las
*Recomendaciones LCD‑CIAI* (sección 10). A completar en conjunto investigadora +
estudiante.

## Clasificación de nivel de riesgo

**Nivel 1 (riesgo nulo o mínimo).** Justificación:

- Fuentes históricas públicas (catálogos y fallos de jurado de 1915–1916, prensa de
  época). Sin datos personales de personas vivas ni datos sensibles (Ley 25.326).
- Nombres de artesanas fallecidas hace más de un siglo. El proyecto busca
  visibilizarlas: la difusión es un objetivo, no un riesgo de privacidad.
- Sin modelos predictivos ni perfilamiento. Si se incorpora vinculación de imágenes
  con IA, se reevalúa.

## Sesgos a tener presentes (no algorítmicos, de las fuentes y del recorte)

- **Sesgo de la fuente:** el catálogo y el fallo registran solo lo exhibido y premiado;
  invisibiliza la producción que no llegó a la exposición.
- **Sesgo de transcripción:** nombres y localidades con grafías inciertas
  (`J`/`I`, `Panci`/`Panei`). Las decisiones de fusión quedan documentadas y son
  reversibles (`revision_duplicados.xlsx`, `docs/bitacora.md`).
- **Sesgo de georreferenciación:** asignar un topónimo actual a una localidad de 1915
  puede forzar equivalencias. `nombre_ciudad` (histórico) se conserva siempre aparte
  de `nombre_ciudad_hoy`.
- **Atribución de género:** se infiere del nombre de pila. Las instituciones llevan `F`
  por convención y todavía no tienen una marca propia en los datos (decisión pendiente
  con la dirección); el explorador y el EDA las reconocen por el comienzo del nombre
  (`INSTITUCION` en `src/pipeline/_util.py`).

## Resguardo

- Datos y código en repositorio institucional / GitHub del proyecto.
- Imágenes de archivo fuera del repositorio (`.gitignore`), en el resguardo acordado
  con la dirección.
- Si se usan asistentes de IA o APIs externas, no se envían más que datos ya públicos.
