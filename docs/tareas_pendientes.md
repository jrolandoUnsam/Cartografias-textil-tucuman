# Tareas pendientes


## IA sobre fotos (objetivo específico 3 del formulario)

El formulario pide "explorar estrategias de vinculación entre registros textuales e
imágenes históricas para la identificación de los textiles presentes en imágenes" (y, en
el plan de trabajo, una "vinculación preliminar entre imágenes y registros escritos").
Hecho hasta ahora: cada obra está vinculada con la página escaneada del catálogo donde
figura (981/981, `05`) y 13 de las 14 piezas del álbum de 1915 están identificadas a mano
en el catálogo (`album_1915.csv`). La identificación automática en las fotos no se hizo.

- [ ] Prueba acotada: con un modelo abierto de detección/segmentación, contar las piezas
  de cada foto del álbum y comparar contra `decisiones/album_1915.csv` (piezas
  transcriptas por LM). Registrar modelo, versión y parámetros (Lineamientos, art. 19) y
  reevaluar el riesgo en `evaluacion_riesgos.md`.


## Geografía

- [ ] **16 de 74 ciudades siguen sin coordenadas** en
  `decisiones/coordenadas_ciudades.csv` (58 cargadas). Completar las que se puedan y
  fijar un criterio para las ambiguas o desconocidas.

## Imágenes
- [ ] Decidir cuál de las dos tomas del álbum de 1915 es la de referencia y registrar
  de qué documento físico salió cada foto (hoja `Fuentes`).

## Entregables de la optativa

- [ ] **Figuras del EDA.** El objetivo específico 2 del formulario (visualizaciones y
  mapas interactivos) lo cubren `outputs/explorador.html` y `outputs/mapa_procedencias.html`.
  Las figuras del EDA (categorías, comparación entre concursos, provincias, expositoras)
  viven sólo dentro del notebook; el informe final no las usa. Falta decidir si se
  exportan. El objetivo 3 está en *IA sobre fotos*.
