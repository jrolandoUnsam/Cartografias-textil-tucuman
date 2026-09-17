# Imágenes de archivo (fuera del repositorio)

Los escaneos (`*.jpg`, `*.JPG`) están en `.gitignore` por peso. Se resguardan aparte,
en el espacio acordado con la dirección del proyecto.

## Conjuntos

| carpeta | contenido |
|---|---|
| `catalogos/1915- catálogo primer concurso tejidos/` | escaneo del catálogo del 1er Concurso Provincial (1915) |
| `catalogos/1915- primer concurso prov tejidos y bord- fallo jurado/` | escaneo del fallo del jurado (1915) |
| `catalogos/1916- catálogo interprov de tejidos y bord/` | escaneo del catálogo del Concurso Interprovincial (1916) |
| `albumes/1915-album-version-1/` | fotografías del álbum de 1915, tomadas con teléfono (2025‑05‑08) |
| `albumes/1915-album-version-2/` | fotografías del álbum de 1915, tomadas con cámara (DSCN5149–5170) |

Los dos álbumes son **dos tomas distintas del mismo material**, no duplicados de los
catálogos: no comparten ningún nombre de archivo con `catalogos/`. Antes vivían en una
carpeta `Imágenes/` en la raíz del proyecto; se movieron acá para que todo el material
de archivo esté bajo `data/raw/`.

Pendiente: decidir cuál de las dos tomas es la de referencia y registrar de qué
documento físico salió cada foto (hoja `Fuentes` de la tabla normalizada).
