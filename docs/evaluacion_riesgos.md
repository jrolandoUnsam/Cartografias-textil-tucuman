# Evaluación de riesgos: sesgo y privacidad

Según los *Lineamientos para la gobernanza de datos e IA de la UNSAM* (arts. 8 a 19) y
las *Recomendaciones LCD‑CIAI* (sección 10 y anexo, sección 6).

## Clasificación de nivel de riesgo

**Nivel 1 (riesgo nulo o mínimo, art. 19).** Justificación:

- Fuentes históricas públicas (catálogos y fallo del jurado de 1915–1916, prensa de
  época). Sin datos personales de personas vivas ni datos sensibles.
- Nombres de artesanas fallecidas hace más de medio siglo. El proyecto busca
  visibilizarlas: la difusión es un objetivo, no un riesgo de privacidad.
- El pipeline no usa modelos de IA, predictivos ni de perfilamiento.
- El único uso de IA fue un asistente de programación, que el art. 19 da como ejemplo
  de Nivel 1 ("herramientas para optimización de código"). 

**Cuándo se reevalúa:**

- si se incorpora un modelo sobre las imágenes (quedó como trabajo futuro o incompleto).


## Requisitos del Nivel 1 (art. 19) y dónde se cumplen

| Requisito | Cómo se cumple |
|---|---|
| Documentación mínima del proceso | `README.md`, `src/pipeline/README.md`, `docs/bitacora.md` (qué se decidió, por qué y quién), `docs/diccionario_datos.md`. |
| Registro de modelos, versiones y parámetros | No hay modelos. |
| Buenas prácticas de seguridad informática | Sin credenciales ni secretos en el repositorio (`.gitignore` excluye `.env`). |
| Uso de datos no personales o anonimizados | Personas históricas, fuentes públicas. |

## Sesgos a tener presentes (no algorítmicos: de las fuentes y del recorte)

- **Autoría que se diluye en las instituciones:** las obras de escuelas, asilos y
  colegios religiosos (10 registros) figuran a nombre de la institución. Las fuentes no
  dicen quiénes las hicieron (probablemente alumnas, asiladas o religiosas), así que ese
  trabajo queda sin nombre propio. Se marcan con `Género = I` para no contarlas como
  mujeres ni como varones.
- **Sesgo de transcripción:** nombres y localidades con grafías inciertas
  (`J`/`I`, `Panci`/`Panei`). Las fusiones quedan documentadas y son reversibles
  (`data/interim/decisiones/fusiones_expositoras.csv`, con el comentario de la revisión
  que las originó, y `docs/bitacora.md`).
- **Sesgo de georreferenciación:** asignar un topónimo actual a una localidad de 1915
  puede forzar equivalencias. `nombre_ciudad` (histórico) se conserva siempre aparte
  de `nombre_ciudad_hoy`, y las ubicaciones deducidas o tentativas se marcan.
- **Atribución de género:** se infiere del nombre de pila; los registros no lo dicen. Las
  instituciones llevan `I`, por la regla `INSTITUCION` (`src/pipeline/_util.py`) o por
  decisión registrada en `nombres_expositoras.csv`. El explorador lo aclara junto al
  filtro y en el análisis por género.
- **Parentescos:** las coincidencias de apellido (`12_redes`) se muestran como pistas,
  nunca como datos, porque las fuentes no registran parentescos.



## Resguardo y publicación

- **Código y datos:** repositorio de GitHub del proyecto, en una cuenta personal del
  estudiante (no es infraestructura institucional). El destino previsto para la
  publicación permanente es el entorno del CIAI (Recomendaciones, anexo 10, art. 9).
- **Escaneos de los catálogos y del fallo:** fuera del repositorio (`.gitignore`), en el
  resguardo acordado con la dirección.
- **Fotografías del álbum de 1915:** **seis sí están en el repositorio**
  (`src/pipeline/plantillas/album/`) y van incrustadas en `outputs/explorador.html`, de
  modo que se difunden con él.
- **Visitantes del explorador:** el mapa base se carga de los servidores de Esri, que
  reciben la dirección IP de quien abre el mapa. El resto (bibliotecas, tipografías,
  datos e imágenes) va dentro del archivo.

