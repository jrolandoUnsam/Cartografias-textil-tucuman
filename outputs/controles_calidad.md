# Controles de calidad de la base

Generado por `src/pipeline/14_controles.py` en cada corrida del pipeline. Lista casos para revisar; no corrige nada. Las páginas (DSCN…) son los escaneos del catálogo o del fallo.

## Resumen

| Grupo | Control | Casos | Qué hacer |
|---|---|--:|---|
| Personas | Nombres parecidos que esperan respuesta de LM | 7 | Volver a preguntarle a LM o darlos por distintos |
| Personas | Mismo nombre, dos registros | 4 | Confirmar que la separación es a propósito |
| Personas | Sin nombre de pila | 5 | Buscar el nombre completo en el fallo o la prensa |
| Personas | Dos personas en un registro | 0 | Decidir si se separan |
| Personas | Parece institución pero tiene género de persona | 2 | Decidir si es persona o institución |
| Personas | Género vacío o desconocido | 0 | Completar en `nombres_expositoras.csv` |
| Personas | Signos de duda en el nombre | 0 | Revisar contra el escaneo |
| Lugares | Sólo provincia con una localidad de la misma expositora | 0 | Elegir la localidad a mano |
| Lugares | Localidades sin coordenadas | 8 | Ubicar o dejar como desconocida |
| Lugares | Ubicaciones tentativas o ambiguas | 1 | Confirmar con LM o con fuentes |
| Lugares | Varios lugares del catálogo, una misma localidad actual | 10 | Confirmar que la separación es a propósito |
| Lugares | Expositora en dos provincias | 1 | Revisar la fusión |
| Lugares | Expositora en varias localidades de una provincia | 13 | Revisar si es el mismo lugar escrito distinto |
| Números de orden y páginas | N.º de orden repetido en la misma sección | 0 | Corregir contra el escaneo |
| Números de orden y páginas | Huecos en la numeración de una sección | 2 | Mirar el escaneo de esa sección |
| Números de orden y páginas | N.º fuera del rango de su página | 0 | Corregir página o número |
| Números de orden y páginas | El índice de páginas no coincide con las obras | 0 | Mirar el escaneo y corregir el número o el índice |
| Premios | La expositora del premio no es la de la obra | 0 | Corregir el vínculo |
| Premios | Obra con más de un premio | 0 | Confirmar |
| Premios | Premio a una obra fuera de concurso | 0 | Revisar vínculo o marca |
| Premios | N.º del fallo distinto del N.º del catálogo | 1 | Revisar |
| Premios | Nombre del fallo muy distinto del catálogo | 1 | Confirmar la identidad |
| Premios | Lugar del fallo distinto del catálogo | 4 | Revisar |
| Premios | Premio repetido en el fallo | 0 | Revisar contra el fallo |
| Premios | Premios sin obra en el catálogo | 13 | Nada, salvo los pendientes |
| Transcripción | Descripción vacía o muy corta | 0 | Completar desde el escaneo |
| Transcripción | Lecturas dudosas en la descripción | 0 | Revisar contra el escaneo |
| Transcripción | Lecturas dudosas en el lugar | 1 | Revisar |
| Transcripción | Obras sin página escaneada | 0 | Asignar página |

## Personas

### Nombres parecidos que esperan respuesta de LM

Pares del detector de duplicados (`02_candidatos`) que se le mandaron a LM y no contestó. Los otros 29 pares sin anotar son los que Julián dio por personas distintas el 25/10 (mismo apellido, otro nombre de pila) y no se listan.

| id A | Nombre A | id B | Nombre B | Parecido |
|---|---|---|---|---|
| 325 | María Fernández | 334 | Arsenia Fernández | 88 |
| 2 | Marina Belmonte | 45 | Máxima Belmonte | 87 |
| 390 | Audelina y Abigail Gómez | 409 | María Abigail Gómez | 83 |
| 215 | Lidia Moya Escobar | 474 | Lastenia Moya Escobar | 82 |
| 129 | María Díaz | 176 | María Cruz Díaz | 80 |
| 435 | Rosa Ariza | 506 | Rita Ariza | 80 |
| 466 | Julia M. Chirou | 468 | Paulina P. de Chirou | 80 |

### Mismo nombre, dos registros

Nombres idénticos (sin contar tildes ni mayúsculas) con distinto id: o falta unirlos o son homónimas que se decidió mantener separadas.

| id | Nombre | Obras |
|---|---|---|
| 255 | Delina I. de Román | 1 |
| 264 | Delina I. de Román | 3 |
| 161 | Delina J. de Román | 1 |
| 209 | Delina J. de Román | 2 |

### Sin nombre de pila

Registradas sólo como "Sra. de…" o "Sta. …": difíciles de unir con otras apariciones de la misma persona. "Sta." puede ser señorita o Santa.

| id | Nombre | Obras |
|---|---|---|
| 48 | Sta. Sandés | 1 |
| 80 | Sra. de Plaza | 2 |
| 359 | Sra. de Puig | 1 |
| 386 | Sta. Guerineau | 1 |
| 394 | Sra. de Serrano | 3 |

### Dos personas en un registro

Nombres con "y" / "e" que no son instituciones. Los 6 conocidos (Cuello, Díaz y Bazán, Gramajo, Gómez, Blay, Vivolo y Cerrasuolo) quedan como registro conjunto (LM 2026-10-28) y no se listan.

Ningún caso.

### Parece institución pero tiene género de persona

El nombre menciona una escuela, asilo, colegio… y no lleva `I`. Puede ser una persona de esa institución ("Mamerta Monteros [Escuela Sarmiento 1915]").

| id | Nombre | Género |
|---|---|---|
| 108 | Mamerta Monteros [Escuela Sarmiento 1915] | F |
| 253 | India de la Misión Franciscana de Nueva Pompeya | F |

### Género vacío o desconocido

Valores fuera de F / M / I.

Ningún caso.

### Signos de duda en el nombre

Un "?" o un paréntesis indica una lectura dudosa. (Los corchetes son variantes ya acordadas con LM.)

Ningún caso.


## Lugares

### Sólo provincia con una localidad de la misma expositora

Obras con sólo la provincia cuando la misma expositora tiene una localidad en esa provincia. `06` ya pasó 53 obras a su localidad; acá quedan las que no pudo resolver (dos localidades posibles).

Ningún caso.

### Localidades sin coordenadas

Lugares que el mapa no puede ubicar en su punto (van al de la provincia, o a ninguno).

| id | Lugar | Provincia | Obras | Nota |
|---|---|---|---|---|
| 14 | S/d | s/d | 1 | el catálogo no indica procedencia |
| 19 | Los Mendoza | Tucumán | 1 | Los Mendoza: quizás en Simoca (sin confirmar); sin punto de ciudad |
| 60 | Rosario | s/d | 5 |  |
| 72 | Santa Rosa | s/d | 2 |  |
| 73 | Orán | s/d | 24 | LM 9-10: puede ser Orán de Tucumán o de Salta; lugar y provincia sin definir |
| 76 | Villa Nueva | s/d | 2 | provincia sin definir: Tucumán o Córdoba |
| 78 | Concordia | s/d | 1 | LM 9-10: provincia sin definir |
| 81 | La Banda | s/d | 3 | LM 9-10: provincia sin definir |

### Ubicaciones tentativas o ambiguas

Coordenadas marcadas `tentativa` o nombre actual con "?" u "o" (dos candidatas).

| id | En el catálogo | Hoy | Provincia | Nota |
|---|---|---|---|---|
| 24 | Leales | Villa de Leales | Tucumán | LM 9-10: Villa de Leales (la ciudad más antigua), tentativo |

### Varios lugares del catálogo, una misma localidad actual

Ids distintos que hoy son el mismo lugar (p. ej. dos ingenios en Banda del Río Salí). Puede ser a propósito (se conserva cómo lo escribió el catálogo) o una fusión pendiente.

| id | En el catálogo | Hoy | Obras |
|---|---|---|---|
| 12 | Ingenio Concepcion | Banda del Río Salí | 18 |
| 75 | Ingenio Guzman | Banda del Río Salí | 1 |
| 25 | Cafayate Salta | Cafayate | 2 |
| 51 | Cafayate | Cafayate | 3 |
| 35 | Escuela Ernesto E. Padilla, Concepcion | Concepción | 1 |
| 59 | Concepcion | Concepción | 14 |
| 67 | Medinas | Medinas | 2 |
| 74 | Medinas, Gucheas | Medinas | 7 |
| 2 | San Miguel de Tucumán | San Miguel de Tucumán | 356 |
| 11 | Asilo Maternal Ciudad | San Miguel de Tucumán | 3 |

### Expositora en dos provincias

La misma persona con obras de provincias distintas: puede haberse mudado, o la fusión unió a dos personas distintas.

| id | Expositora | Lugares | Años |
|---|---|---|---|
| 199 | Carmen Pérez | Salta (Cerrillos); Tucumán (Atahona) | 1916 |

### Expositora en varias localidades de una provincia

Puede ser real (vivía en un lugar y envió desde otro, o el catálogo nombra el departamento en un año y el pueblo en otro).

| id | Expositora | Localidades | Años |
|---|---|---|---|
| 4 | Dalmira González Sorol | San Miguel de Tucumán, Tafí Viejo | 1915, 1916 |
| 19 | Mercedes del Moral | Monteros, San Miguel de Tucumán | 1915, 1916 |
| 70 | María Cleofé de Bustamante | Simoca, Yacuchiri | 1915, 1916 |
| 107 | Dominga Villoldo | San Miguel de Tucumán, San Pablo | 1915, 1916 |
| 123 | Manuela Gramajo | Monteagudo, Niogasta | 1916 |
| 127 | Vitalina Zelaya | Monteagudo, San Miguel de Tucumán | 1916 |
| 325 | María Fernández | Concepcion, Medinas, Gucheas | 1916 |
| 334 | Arsenia Fernández | Concepcion, Medinas, Medinas, Gucheas | 1916 |
| 370 | Ángela Sotillo | Arcadia, F.c.n.o.a., San Miguel de Tucumán | 1916 |
| 377 | Josefa López Rivero | Concordia, San Miguel de Tucumán | 1916 |
| 391 | María Calcagni | Concepcion, Graneros | 1916 |
| 409 | María Abigail Gómez | Concepcion, Graneros | 1916 |
| 428 | Ángela Robles | Monteros, Orán | 1916 |


## Números de orden y páginas

### N.º de orden repetido en la misma sección

Dos obras con el mismo número en la misma sección y concurso: error de transcripción o fila duplicada.

Ningún caso.

### Huecos en la numeración de una sección

Números que faltan entre el primero y el último de una sección: obra sin transcribir, número mal leído, o un salto del propio catálogo.

| Año | Sección | Rango | Faltan |
|---|---|---|---|
| 1915 | BORDADO EN BLANCO Y SEDA | 1–13 | 9 |
| 1915 | PAÑUELOS | 1–19 | 17 |

### N.º fuera del rango de su página

El número de la obra no cae entre el primero y el último de la página escaneada que tiene asignada (`Paginas_Catalogo`): la página o el número están mal.

Ningún caso.

### El índice de páginas no coincide con las obras

`Paginas_Catalogo` dice quién abre y quién cierra cada sección en cada página; acá no coincide con la obra de ese número. Suele ser un número de orden mal transcripto o dos obras invertidas.

Ningún caso.


## Premios

### La expositora del premio no es la de la obra

El premio apunta a una persona y a una obra de otra persona (o a una obra que no existe).

Ningún caso.

### Obra con más de un premio

Puede ser real (premio y accésit) o dos premios del fallo vinculados a la misma pieza por error (el caso de la blusa).

Ningún caso.

### Premio a una obra fuera de concurso

Contradicción: el catálogo dice que la obra no competía.

Ningún caso.

### N.º del fallo distinto del N.º del catálogo

El fallo cita un número y la obra vinculada tiene otro. A veces es a propósito (vínculo por nombre), a veces un error de uno de los dos documentos.

| premio_id | Nombre en el fallo | Sección del fallo | N.º fallo | objeto_id | N.º catálogo | Vínculo |
|---|---|---|---|---|---|---|
| 99 | Dominga Nieva | ESTÍMULO | 9 | 104 | 4 | decisión a mano |

### Nombre del fallo muy distinto del catálogo

El fallo y el catálogo escriben a la persona de forma muy diferente: confirmar que es la misma.

| premio_id | Nombre en el fallo | En la base | Parecido |
|---|---|---|---|
| 62 | Mercedes Pereyra | María Mercedes Pereira | 79 |

### Lugar del fallo distinto del catálogo

El fallo ubica a la premiada en otro lugar que el catálogo: o la obra vinculada es otra, o uno de los documentos se equivoca.

| premio_id | Nombre en el fallo | Lugar en el fallo | objeto_id | Lugar en el catálogo |
|---|---|---|---|---|
| 17 | Melchora Valenzuela | Ciudad | 111 | Simoca |
| 35 | Rosa Valenzuela | CIUDAD | 135 | Simoca |
| 73 | Elvira Rodríguez | SAN RAFAEL | 90 | S/d |
| 93 | Ana tactagi | Simoca | 57 | San Miguel de Tucumán |

### Premio repetido en el fallo

Mismo nombre, sección, premio, objeto y N.º en dos filas: el fallo premió dos piezas iguales o la fila se transcribió dos veces.

Ningún caso.

### Premios sin obra en el catálogo

Fuera de catálogo o pendientes de vincular (informativo).

| premio_id | Nombre en el fallo | Premio | Sección | Objeto en el fallo | Estado |
|---|---|---|---|---|---|
| 6 | Dominga Castaño | Premio de 50 | FRAZADA DE LANA | frazada | fuera de catálogo |
| 15 | Lujarda J. de González | Premio de 20 | FRAZADA DE LANA | frazada | fuera de catálogo |
| 16 | Lujarda J Gonzalez | Premio de 20 | FRAZADA DE LANA | frazada | fuera de catálogo |
| 18 | Melchora Valenzuela | Premio de 20 | FRAZADA DE LANA | frazada | fuera de catálogo |
| 39 | Lujarda J. de González | Premio de 10 | Jergón | Jergón | fuera de catálogo |
| 63 | Rosa Barceló | Premio de 25 | CROCHET E IRLANDA | CROCHET E IRLANDA | fuera de catálogo |
| 66 | Dalmira González Sorol | Premio de 50 | DESHILADO | Mantel de altar | fuera de catálogo |
| 67 | Hermanas domínicas | Premio de 25 | DESHILADO | blusa | fuera de catálogo |
| 76 | Marina Belmonte | Premio de 20 | Accésit |  | fuera de catálogo |
| 80 | Alejandrina Peiró | Premio de 25 | BORDADO EN BLANCO Y SEDA |  | fuera de catálogo |
| 86 | Lucrecia Carrazan | Premio de 25 | ESTÍMULO | colcha de filet | fuera de catálogo |
| 89 | Amicia Diaz | Premio de 10 | ESTÍMULO | frazada | fuera de catálogo |
| 103 | Catalina de Figueroa | Premio de 30 | nan |  | fuera de catálogo |


## Transcripción

### Descripción vacía o muy corta

Obras sin texto o con menos de 4 letras.

Ningún caso.

### Lecturas dudosas en la descripción

Textos con "?", corchetes, "s/d" o "ilegible": quien transcribió no estaba seguro.

Ningún caso.

### Lecturas dudosas en el lugar

El lugar transcripto tiene "?", paréntesis o "s/d".

| objeto_id | Año | Expositora | Lugar en el documento | Lugar en la base | Página |
|---|---|---|---|---|---|
| 90 | 1915 | Elvira Rodríguez They | S/D | S/d | DSCN5180.JPG |

### Obras sin página escaneada

No se puede ir a la fuente.

Ningún caso.
