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
- No se cruza con RENATRA (tarea 4 del formulario; decisión del 30/10/2026). Ese cruce
  habría sumado datos de artesanas vivas y obligaría a reevaluar el nivel.

## Sesgos a tener presentes (no algorítmicos, de las fuentes y del recorte)

- **Sesgo de la fuente:** el catálogo y el fallo registran solo lo exhibido y premiado;
  invisibiliza la producción que no llegó a la exposición.
- **Sesgo de transcripción:** nombres y localidades con grafías inciertas
  (`J`/`I`, `Panci`/`Panei`). Las decisiones de fusión quedan documentadas y son
  reversibles (`data/interim/decisiones/fusiones_expositoras.csv`, con el comentario de
  la revisión que las originó, y `docs/bitacora.md`).
- **Sesgo de georreferenciación:** asignar un topónimo actual a una localidad de 1915
  puede forzar equivalencias. `nombre_ciudad` (histórico) se conserva siempre aparte
  de `nombre_ciudad_hoy`.
- **Atribución de género:** se infiere del nombre de pila; los registros no lo dicen. Las
  instituciones llevan `I`, una marca propia en lugar de género (pedido de LM, 28/10),
  asignada a las que reconoce la regla `INSTITUCION` (`src/pipeline/_util.py`). El
  explorador permite filtrar por género y lo aclara en "Lo que el archivo no dice".
- **Parentescos:** las coincidencias de apellido (`12_redes`) se muestran como pistas,
  nunca como datos, porque las fuentes no registran parentescos.

## Resguardo

- Datos y código en repositorio institucional / GitHub del proyecto.
- Imágenes de archivo fuera del repositorio (`.gitignore`), en el resguardo acordado
  con la dirección.
- Si se usan asistentes de IA o APIs externas, no se envían más que datos ya públicos.
