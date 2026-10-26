# Relevamiento de prensa y archivo: qué se tomó de cada fila

Las tres hojas "no …" del Excel crudo no entran al pipeline. Este documento las repasa
fila por fila (número de fila de la hoja, sin contar el encabezado) y dice qué se
aprovechó y dónde quedó. Revisión del 2026-10-25.

Destinos:

- **Fuentes**: filas 4, 5 y 6 de la hoja `Fuentes` (tabla manual).
- **Concursos**: columnas `fecha_decreto`, `fecha_inauguracion`, `fecha_fallo`, `sede`,
  `organizacion` y `notas_fechas` de la hoja `Concursos` (tabla manual).
- **Menciones**: `data/interim/decisiones/menciones_prensa.csv`.
- **LM**: pregunta para Larisa (`docs/tareas_pendientes.md`).
- **Contexto**: sirve para el informe, no para la base.
- **Nada**: no trata de los concursos ni de las expositoras.

## Hoja `no PRENSA-EL ORDEN` (37 filas, fuente 4)

| fila | fecha | título | qué se tomó |
|--:|---|---|---|
| 1 | 8/7/1915 | El Dr Cárcano | Nada |
| 2 | 10/7/1915 | El Dr Cárcano | Nada |
| 3 | 12/7/1915 | Las conferencias de Lugones | Nada (sin transcripción) |
| 4 | 14/7/1915 | En la Sarmiento. Conferencias de Lugones | Nada (sin transcripción) |
| 5 | 15/7/1915 | El curanderismo en la campaña | Nada (sin transcripción) |
| 6 | 15/7/1915 | Telares en las escuelas | Menciones (Monteros, La Cocha) y Contexto: telares criollos en escuelas de Monteros, La Cocha, Río Colorado y Ciudadela |
| 7 | 21/7/1915 | Las fábricas de tejidos | Contexto: fábricas de Buenos Aires, 3183 mujeres y 475 que trabajan a domicilio |
| 8 | 21/7/1915 | Dr. Norberto Piñero | Nada |
| 9 | 24/7/1915 | La conferencia del sr Onelli | Contexto (Onelli, ver Archivo Padilla) |
| 10 | 26/7/1915 | La Mujer en Tucumán (Miss Terieuse) | Contexto: debate sobre la vida intelectual de las mujeres |
| 11 | 28/7/1915 | Una carta abierta | Contexto (respuesta a la anterior) |
| 12 | 28/7/1915 | Industrias domésticas | Concursos (decreto del 21/7, fecha prevista 24/9, comisión de damas) y Menciones (Acuña Zavalía en la comisión) |
| 13 | 11/9/1915 | Ecos del día. El pueblo en el Centenario | Nada (sin transcripción) |
| 14 | 11/9/1915 | El mitin de mañana | Nada (sin transcripción) |
| 15 | 15/9/1915 | La acción popular | Nada (sin transcripción) |
| 16 | 15/9/1915 | Labores domésticas | Concursos (postergación al 29/9, cierre el 23/9) |
| 17 | 17/9/1915 | Concurso de tejidos. Exposición postergada | Concursos (ídem) |
| 18 | 20/9/1915 | Frente al Centenario | Nada (sin transcripción) |
| 19 | 21/9/1915 | Bolivia en el centenario | Nada (sin transcripción) |
| 20 | 27/9/1915 | Comisión del Centenario | Nada (sin transcripción) |
| 21 | 27/9/1915 | Labores domésticas. Próxima exposición | Concursos (sede, hora, entrada libre, duración, venta de obras) y Menciones (Colegio de la Sagrada Familia = Mercedes Pacheco). Tiene foto de la comisión de damas |
| 22 | 30/9/1915 | Primer concurso… El acto inaugural | Concursos (sede "Museo y Archivos", comisión) |
| 23 | 30/9/1915 | ídem | Menciones (Sorroza, González Sorol, Dominga Lescano). La observación dice "misma referencia a lo que dijo Ana Toledo, ver entrevista": esa entrevista no está en el repositorio → LM |
| 24 | 30/9/1915 | ídem | Menciones (poncho de la Sagrada Familia, colchas de las Cuello, traje Richelieu, Mayer, alba de González Sorol, alfombra de Acuña Zavalía) |
| 25 | 30/9/1915 | ídem | Contexto: lista de asistentes a la inauguración. De ellas sólo Isabel Bascary de Acuña Zavalía es expositora |
| 26 | 18/7/1916 | Notas de Arte. La exposición Terragni | Nada (sin transcripción) |
| 27 | 19/7/1916 | Industrias manuales | Concursos (fallo del 18/7/1916) y Contexto (las provincias vecinas, la industria "en estado vegetativo") |
| 28 | 16/8/1916 | El desnudo en el arte | Nada |
| 29 | 17/8/1916 | El desnudo en el arte | Nada |
| 30 | 23/8/1916 | En la Escuela P. de Mujeres | Menciones (Escuela Profesional de Mujeres; no habla de sus tejidos) |
| 31 | 26/8/1916 | En la escuela Rivadavia. Exposición de economía doméstica | Contexto (sin transcripción; la escuela no es expositora) |
| 32 | 6/9/1916 | La escuela intermedia | Nada |
| 33 | 6/9/1916 | La escuela intermedia | Contexto: la escuela de Catamarca teje en sus propios telares |
| 34 | 29/9/1916 | La demostración a la señora Elvira S. de Padilla | Contexto: homenaje por su actuación en las fiestas del Centenario |
| 35 | 10/10/1916 | La randa tucumana | Menciones (Orán) → LM (¿Tucumán o Salta?) |
| 36 | 10/10/1916 | ídem | Menciones (Orán) |
| 37 | 10/10/1916 | ídem | Contexto: una randa llevada a Europa; Padilla y el fomento de la industria |

## Hoja `no ARCHIVO PADILLA` (81 filas, fuente 5)

| filas | qué son | qué se tomó |
|---|---|---|
| 5 | foto del 29/9/1915 en el concurso, con Lucila López Islas como "presidenta de la comisión"; "es la imagen que pertenece al álbum" | Fuentes, Concursos (contradice a la prensa, que da como presidenta a Leston de Guzmán) → LM |
| 6 | boletín del concurso interprovincial (julio 1916), "tiene las fotos del álbum"; "ver transcripción en otra pestaña" | Fuentes. La pestaña con la transcripción no está en el crudo → LM. Si las fotos del "álbum de 1915" salen de este boletín de 1916, hay que revisar el nombre → LM |
| 69 | carta a Onelli, 2/11/1915: le manda "los relatos oficiales del último concurso de tapices y bordados criollos" | Fuentes |
| 62, 64, 65, 73 | cartas de Padilla (padre e hijo) con Onelli, 1921-1923: la empresa "Onelli Alfombras Ltda." y una colcha de una "comprovinciana pobre" para vender en $210 | Contexto: qué pasó con estas artesanías después de los concursos |
| 4, 16 | fotos de Padilla con Cárcano (mayo 1915) | Nada |
| 7, 8 | escuela "Tomasa de la Quintana Escalada" (1941), exceso de maestras normales (1929-1930) | Nada |
| 44 | Liga Patriótica: escuelas en fábricas | Nada |
| 49 | María Elvira Rojas, cátedra de encuadernación (1951) | Nada |
| 78 | indígenas de la colonia Cushamen, Chubut (1940) | Nada |
| 1-3, 9-15, 17-43, 45-48, 50-61, 63, 66-68, 70-72, 74-77, 79-81 | correspondencia política y personal (Cárcano, Piñero, Rojas, Llobet, Onelli, Carlés; la 63 es sobre el garbanzo), sin relación con los concursos | Nada |

## Hoja `no Prensa-Rakow lib` (3 filas, fuente 6)

| fila | qué es | qué se tomó |
|--:|---|---|
| 1 | Páez de la Torre (1986), "21 de julio de 1915: muestra regional de Tejido y Bordado": "la primera vez" que se valoraron estas artesanías | Fuentes |
| 2 | el local de 24 de Septiembre 871 | Concursos (sede) |
| 3 | "Menciona a las premiadas" | Nada: no hay transcripción para cotejar con el fallo |

## Lo que falta y no está en el repositorio

- La entrevista a Ana Toledo que cita la fila 23 de El Orden.
- La transcripción del boletín de 1916 (Archivo Padilla, fila 6).
- El texto completo de la nota de Páez de la Torre y el medio donde se publicó.
- El repositorio del Archivo Padilla y qué quiere decir la sigla "AHT".
