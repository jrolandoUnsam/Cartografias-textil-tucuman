# Auditoría de comentarios — estado de aplicación

_Generado por `src/pipeline/audit_comentarios.py` — no editar a mano._

Compara cada decisión anotada a mano contra el estado actual de `data/processed/tabla_normalizada.xlsx`.

**Hallazgo global:** la hoja `Objetos` es **idéntica** a la copia congelada (`tests/golden/`): ningún `expositora_id` se reasignó, así que **ninguna fusión de expositoras se aplicó a la tabla**. Sí se normalizaron 437 nombres.

**Veredictos:**
- `SIN HACER` — la fila sigue igual que en el golden.
- `SOLO NOMBRE` — se corrigió/normalizó el nombre, pero las dos filas **siguen sin fusionar** (los objetos no se movieron).
- `SOLO NOMBRE · OBJETOS PARTIDOS` — ídem, y además hay objetos en la fila que el comentario manda descartar → fusionar no es solo borrar.
- `FUSIÓN OK` — una fila desapareció y quedó la que pide el comentario.
- `FUSIÓN REVISAR` — una fila desapareció pero quedó la otra.
- `OK SEPARAR` — se pidió **no** unificar y siguen las dos filas (correcto).
- `CONTRA LO PEDIDO` — se pidió separar y se fusionó, o al revés.

## 1. `revision_duplicados.xlsx` — hoja *Personas - candidatos*

_Conteo:_ FUSIÓN OK: 6 · OK SEPARAR: 8 · SOLO NOMBRE: 55

| # | id A / nombre | id B / nombre | Hecho | Comentario | Decisión leída | Estado actual | Veredicto |
|---|---|---|---|---|---|---|---|
| 1 | `126` Gregoria Luna | `269` Gregoria Luna | True | son la misma | Unificar (cualquiera de las dos) | 2 filas · A:10 obj, B:0 obj | **SOLO NOMBRE** |
| 2 | `223` Elisa B. de Gramajo | `408` Elisa B. de Gramajo | True | son la misma | Unificar (cualquiera de las dos) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 3 | `244` Edelmira A. de Moreno | `279` Edelmira A. de Moreno | True | son la misma | Unificar (cualquiera de las dos) | 2 filas · A:10 obj, B:0 obj | **SOLO NOMBRE** |
| 4 | `16` Palmira Contreras | `426` Palmira Contreras | True | dejamos b | Unificar → conservar B (426) | 2 filas · A:3 obj, B:0 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 5 | `40` Enriqueta Fronzuti | `461` Enriqueta Fronzuti | True | dejamos b | Unificar → conservar B (461) | 2 filas · A:7 obj, B:0 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 6 | `82` Ángeles Cuadrado | `514` Ángeles Cuadrado | True | dejamos a | Unificar → conservar A (82) | 2 filas · A:4 obj, B:0 obj | **SOLO NOMBRE** |
| 7 | `25` Concepción y Rosa Cuello | `282` Concepción y Rosa Cuello | True | son la misma, dejamos con tilde | Unificar → conservar A (25) | 2 filas · A:36 obj, B:0 obj | **SOLO NOMBRE** |
| 8 | `35` María J. de Aguirre | `373` María J. de Aguirre | False | J o I? Visto en fotos / lo unifiqué con la J. no vi el I, ¿sería del catálogo? | Unificar (cualquiera de las dos) | 2 filas · A:4 obj, B:0 obj | **SOLO NOMBRE** |
| 9 | `59` Lorenza V. de Panei | `252` Lorenza V. de Panei | False | unificamos panei para que se identifique que es la misma y porque es apellido más común, pero dejaremos registro de la elección | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE** |
| 10 | `102` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | `117` — | True | Escuela y Hogar de Obreras de la Sociedad de Beneficencia | Unificar (cualquiera de las dos) | 1 fila: 102 (Escuela y Hogar de Obreras de la Sociedad de Beneficencia) · 14 obj | **FUSIÓN OK** |
| 11 | `121` Tránsito Soaje de Ree | `381` Tránsito Soaje de Ree | True | dejamos con tilde | Unificar → conservar A (121) | 2 filas · A:4 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 12 | `196` Concepción de Pérez | `319` Concepción de Pérez | True | dejamos con tilde | Unificar (cualquiera de las dos) | 2 filas · A:2 obj, B:1 obj | **SOLO NOMBRE** |
| 13 | `270` Felisa R. de Sánchez | `278` Felisa R. de Sánchez | True | dejamos con tilde | Unificar → conservar A (270) | 2 filas · A:9 obj, B:0 obj | **SOLO NOMBRE** |
| 14 | `286` Superiora del Colegio Santa Rosa de Viterbo | `492` Superiora del Colegio Santa Rosa de Viterbo | True | dejamos b | Unificar → conservar B (492) | 2 filas · A:0 obj, B:2 obj | **SOLO NOMBRE** |
| 15 | `313` Concepción de Pérez | `319` Concepción de Pérez | True | dejamos con tilde | Unificar → conservar B (319) | 2 filas · A:0 obj, B:1 obj | **SOLO NOMBRE** |
| 16 | `329` María Slopart de Llavi | `345` María Slopart de Llavi | True | dejamos con tilde | Unificar → conservar B (345) | 2 filas · A:0 obj, B:2 obj | **SOLO NOMBRE** |
| 17 | `3` Isaura S. de Risso Patrón | `442` Isaura S. de Risso Patrón | True | dejamos A | Unificar → conservar A (3) | 2 filas · A:3 obj, B:0 obj | **SOLO NOMBRE** |
| 18 | `12` Lastenia Barrero | `120` Lastenia Barrero | False | Dejamos barrero, fue una figura importante | Unificar → conservar B (120) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 19 | `70` María Cleofé de Bustamante | `213` María Cleofé de Bustamante | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (70) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 20 | `117` — | `450` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | True | Escuela y Hogar de Obreras de la Sociedad de Beneficencia (ídem arriba) | Unificar (cualquiera de las dos) | 1 fila: 450 (Escuela y Hogar de Obreras de la Sociedad de Beneficencia) · 0 obj | **FUSIÓN OK** |
| 21 | `139` Edelmira C. de Roldán | `261` Edelmira C. de Roldán | True | dejamos con tilde | Unificar → conservar B (261) | 2 filas · A:0 obj, B:0 obj | **SOLO NOMBRE** |
| 22 | `161` Delina J. de Román | `209` Delina J. de Román | False | MUY POLÉMICO. este no lo unificaría, no queda claro si son la misma persona o un familiar que podía prestarle lana de vicuña para tejer. total al momento de buscar info de vicuña se verá el matiz. por ahora lo dejaría así hasta más info a futuro- | Mantener SEPARADAS | 2 filas · A:1 obj, B:2 obj | **OK SEPARAR** |
| 23 | `161` Delina J. de Román | `264` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:3 obj | **SOLO NOMBRE** |
| 24 | `209` Delina J. de Román | `255` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Unificar (cualquiera de las dos) | 2 filas · A:2 obj, B:1 obj | **SOLO NOMBRE** |
| 25 | `255` Delina I. de Román | `264` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:3 obj | **SOLO NOMBRE** |
| 26 | `8` — | `87` Isabel del Río | True | dejamos con tilde | Unificar → conservar B (87) | 1 fila: 87 (Isabel del Río) · 2 obj | **FUSIÓN OK** |
| 27 | `165` Lorenza de Díaz | `297` Lorenza de Díaz | True | dejamos con tilde | Unificar → conservar B (297) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 28 | `187` Lugarda Juárez | `301` Lugarda Juárez | True | dejamos con tilde | Unificar → conservar B (301) | 2 filas · A:0 obj, B:2 obj | **SOLO NOMBRE** |
| 29 | `194` Ramona de Pérez | `312` Ramona de Pérez | True | dejamos con tilde | Unificar → conservar A (194) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 30 | `221` Segunda Giménez | `268` Segunda Jiménez | False | De momento no las uniría (la vicuña es una práctica tan específica que me da duda, no son dos vicuñas las que mandó) | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 31 | `19` Mercedes del Moral | `441` Mercedes G. del Moral | False | Aparece como de San Miguel 1915 y de Monteros 1916 /lo mantendría como está | Mantener SEPARADAS | 2 filas · A:3 obj, B:1 obj | **OK SEPARAR** |
| 32 | `52` Edelmira C. de Roldán | `261` Edelmira C. de Roldán | True | dejamos el A | Unificar → conservar A (52) | 2 filas · A:8 obj, B:0 obj | **SOLO NOMBRE** |
| 33 | `148` María Salinas | `256` María Salinas | True | dejamos con tilde | Unificar → conservar B (256) | 2 filas · A:0 obj, B:4 obj | **SOLO NOMBRE** |
| 34 | `191` María A. Argañaraz | `302` María A. de Argañaraz | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar B (302) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 35 | `220` Dorotea C. de Lazarte | `308` Dorotea C. de Lazarte | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (220) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 36 | `231` Rita González | `290` Rita González | True | dejamos con tilde | Unificar → conservar A (231) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 37 | `7` — | `32` Ana del Río | True | dejamos con tilde | Unificar → conservar B (32) | 1 fila: 32 (Ana del Río) · 2 obj | **FUSIÓN OK** |
| 38 | `86` Juana Pérez | `465` Juana Pérez | True | dejamos con tilde | Unificar → conservar A (86) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 39 | `115` María Ávila | `222` María Ávila | True | dejamos con tilde | Unificar → conservar A (115) | 2 filas · A:20 obj, B:0 obj | **SOLO NOMBRE** |
| 40 | `118` — | `271` Escuela Profesional de Mujeres | True | dejamos b | Unificar → conservar B (271) | 1 fila: 271 (Escuela Profesional de Mujeres) · 24 obj | **FUSIÓN OK** |
| 41 | `152` Mercedes Ruiz de Arzuaga | `323` Mercedes Ruiz de Arzuaga | True | dejamos el b | Unificar → conservar B (323) | 2 filas · A:0 obj, B:2 obj | **SOLO NOMBRE** |
| 42 | `159` Dorotea C. de Lazarte | `308` Dorotea C. de Lazarte | True | ídem arriba | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:1 obj | **SOLO NOMBRE** |
| 43 | `219` Amelia N. de Plaza | `285` Amelia N. de Plaza | True | dejamos a | Unificar → conservar A (219) | 2 filas · A:1 obj, B:2 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 44 | `260` María Rueda | `283` María Rueda | True | dejamos con tilde | Unificar → conservar B (283) | 2 filas · A:0 obj, B:4 obj | **SOLO NOMBRE** |
| 45 | `373` María J. de Aguirre | `407` María J. de Aguirre | True | unifiqué porque ambos envíos además son irlansa | Unificar (cualquiera de las dos) | 2 filas · A:0 obj, B:1 obj | **SOLO NOMBRE** |
| 46 | `54` Irene C. de Aybar | `284` Irene C. de Aybar | True | dejamos b | Unificar → conservar B (284) | 2 filas · A:3 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 47 | `67` — | `76` Arsenia F. Medina | True | Vamos con Arsenia F. Medina. Veo que no está en el listado, falta la 67, ¿será que hice lío? | Unificar (cualquiera de las dos) | 1 fila: 76 (Arsenia F. Medina) · 2 obj | **FUSIÓN OK** |
| 48 | `295` María Luna | `309` María Luna | True | dejamos con tilde | Unificar → conservar A (295) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 49 | `78` Antonia de Soria | `101` Antonia de Soria | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (78) | 2 filas · A:3 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 50 | `385` M. Luisa Roberti | `400` M. Luisa Roberti | True | dejamos b | Unificar → conservar B (400) | 2 filas · A:0 obj, B:2 obj | **SOLO NOMBRE** |
| 51 | `102` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | `450` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | True | Dejar completo: Escuela y Hogar de Obreras de la Sociedad de Beneficencia | Unificar (cualquiera de las dos) | 2 filas · A:14 obj, B:0 obj | **SOLO NOMBRE** |
| 52 | `161` Delina J. de Román | `255` Delina I. de Román | True | ídem arriba, las dejaría separadas de momento | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 53 | `196` Concepción de Pérez | `313` Concepción de Pérez | True | dejamos con tilde | Unificar → conservar A (196) | 2 filas · A:2 obj, B:0 obj | **SOLO NOMBRE** |
| 54 | `348` Julia M. Chirou | `466` Julia M. Chirou | True | dejamos b | Unificar → conservar B (466) | 2 filas · A:1 obj, B:2 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 55 | `364` Asilo del Buen Pastor | `521` Asilo del Buen Pastor | False | DEL /dejamos del | Unificar → conservar A (364) | 2 filas · A:4 obj, B:2 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 56 | `31` Ana de Tactagi | `55` Ana de Tactagi | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar B (55) | 2 filas · A:2 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 57 | `162` Carmen de Moya | `296` Carmen de Moya | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (162) | 2 filas · A:7 obj, B:3 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |
| 58 | `182` Delina R. Espinosa | `183` Delia Espinosa | True | estas no son la misma, quizás familia porque la tercera en el catálogo es simona espinosa | Mantener SEPARADAS | 2 filas · A:1 obj, B:3 obj | **OK SEPARAR** |
| 59 | `289` Sofía C. González | `470` Sofía C. de González | True | dejamos con tilde, lo unificaría con el de abajo 234, 289, 470 | Unificar → conservar A (289) | 2 filas · A:4 obj, B:0 obj | **SOLO NOMBRE** |
| 60 | `333` Margarita García de Esparré | `354` Margarita G. de Esparré | True | dejamos a | Unificar → conservar A (333) | 2 filas · A:3 obj, B:0 obj | **SOLO NOMBRE** |
| 61 | `52` Edelmira C. de Roldán | `139` Edelmira C. de Roldán | True | Dejamos el que aporta más info A | Unificar → conservar A (52) | 2 filas · A:8 obj, B:0 obj | **SOLO NOMBRE** |
| 62 | `381` Tránsito Soaje de Ree | `389` Tránsito S. de Ree  | True | Dejar el que aporta más info A | Unificar → conservar A (381) | 2 filas · A:1 obj, B:0 obj | **SOLO NOMBRE** |
| 63 | `23` Rosa Alderete | `422` Aurora Alderete | False | Ambas de Montero categoria Randas. Madre e Hija? /ojalá! es para un estudio a futuro hablar con las randeras. Por ahora el único apellido que aparece publicado en una genealogía con randeras es Lorenza Alderete de Núñez. | Mantener SEPARADAS | 2 filas · A:7 obj, B:1 obj | **OK SEPARAR** |
| 64 | `92` Carmen Pereira | `201` Carmen Herrera | True | estos no son el mismo nombre, están unidos por algo en particular? | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 65 | `234` Sofía C. de González | `289` Sofía C. González | False | unifiqué con el más completo | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:4 obj | **SOLO NOMBRE** |
| 66 | `234` Sofía C. de González | `470` Sofía C. de González | False | unifiqué con el más completo | Unificar (cualquiera de las dos) | 2 filas · A:1 obj, B:0 obj | **SOLO NOMBRE** |
| 67 | `409` María Abigail Gómez | `460` María Abigail Gómez | True | Dejar A | Unificar → conservar A (409) | 2 filas · A:5 obj, B:0 obj | **SOLO NOMBRE** |
| 68 | `4` Dalmira González Sorol | `404` Dalmira González Sorol | False | Tafi Viejo en 1915 y Tucumán 1916 /dejaría cada ciudad como está | Mantener SEPARADAS | 2 filas · A:6 obj, B:1 obj | **OK SEPARAR** |
| 69 | `28` Rosario B. d'Empaire | `110` Rosario B. D'Empaire | False | vamos con B | Unificar → conservar B (110) | 2 filas · A:2 obj, B:1 obj | **SOLO NOMBRE · OBJETOS PARTIDOS** |

## 2. `revision_duplicados.xlsx` — hoja *Ciudades - candidatos*

| # | id A / nombre | id B / nombre | Hecho | Comentario | Estado actual | Veredicto |
|---|---|---|---|---|---|---|
| 1 | `26` ASILO CIUDAD | `79` ASILO, CIUDAD | False | — | 2 filas · A:6 obj, B:1 obj | **OK SEPARAR** |
| 2 | `37` LAMADRID | `52` LA MADRID | True | La  Madrid | 1 fila: 52 (LA MADRID) | **FUSIÓN OK** |
| 3 | `62` GUCHEA | `80` GUCHEAS | True | Gucheas | 1 fila: 80 (GUCHEAS) | **FUSIÓN OK** |
| 4 | `9` CÓRDOBA | `63` CORDOBA | True | — | 1 fila: 9 (nan) | **FUSIÓN OK** |

## 3. `tabla_normalizada.xlsx` — hoja *Premios* (filas con comentario)

> Las 8 columnas originales de la hoja Premios están **intactas** respecto del golden. Lo que se agregó son las columnas de vínculo (`persona_id`, `objeto_id`, …, salida de `03b_premios.py`) y las de comentario.
>
> Los comentarios de esta hoja son **observaciones sobre nombres**, no órdenes de fusión. La columna *Nombre real de la expositora* muestra a quién apunta hoy el `objeto_id` de esa fila (vía `Objetos.expositora_id`).

| fila | NOMBRE en el fallo | objeto_id | Nombre real de la expositora (hoy) | Comentario(s) | Estado |
|---|---|---|---|---|---|
| 0 | Angela L. de Diblasi | 108 | Ángela S. de Diblasi | **Mis comentarios:** Angela L. vs Angela S | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 6 | Dominga Castaño | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Son distintas personas para mi / **Coment LM:** coincido | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 8 | Vicenta B. de Medina | 121 | Vicenta V. de Medina | **Mis comentarios:** Vicenta V. vs Vicenta B. / **Coment LM:** quizás podemos normalizar sobre la base del catálogo | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 10 | Maria C. Bustamante | 122 | María Cleofé de Bustamante | **Mis comentarios:** Encontramos segundo nombre / **Coment LM:** buenísimo | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 13 | Lorenza V. de Pérez | 107 | Lorenza V. de Panei | **Mis comentarios:** Parece ser la misma persona. Vista en catalogo como de Panci y Panei | observación / confirmación |
| 14 | Rosa V. de Lescano | 103 | Rosa V. de Lezcano | **Mis comentarios:** Lescano vs Lezcano | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 15 | Lujarda J. de González | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 16 | Lujarda J Gonzalez | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda. Además, es raro porque parece que ganan dos mujeres distintas según las fotos de los premios, una es de Gonzalez y la otra González. | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 20 | Isabel B. de Acuña de Zavalia | 145 | Isabel B. de Acuña Zavalía | **Mis comentarios:** DE Zavalia y tilde en i / **Coment LM:** perfecto, lo dejamos en su versión más completa | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 21 | (Sra.) de Plaza | 140 | Sra. de Plaza | **Mis comentarios:** Sra / **Coment LM:** logré ver lo mismo en el catálogo, genial, ok con sra. | observación / confirmación |
| 28 | Escuela y hogar de obreras de la sociedad de beneficencia | 192 | Escuela y Hogar de Obreras de la Sociedad de Beneficencia | **Mis comentarios:** Misma / **Coment LM:** ok | observación / confirmación |
| 31 | Clemencia Zelarayan | 193 | Clemencia de Zelarayán | **Mis comentarios:** DE + apellido / **Coment LM:** ok | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 35 | Rosa Valenzuela | 135 | Rosa V. de Valenzuela | **Mis comentarios:** V. Aparentemente apellido o segundo nombre / **Coment LM:** ok | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 36 | Arsenia Medina | 134 | Arsenia F. Medina | **Mis comentarios:** F. Aparentemente apellido o segundo nombre / **Coment LM:** ok | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 39 | Lujarda J. de González | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 41 | Dominga Lezcano | 43 | Dominga Lescano | **Mis comentarios:** Lescano vs Lezcano | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 43 | Delicia G. de Robles | 34 | Delina G. de Robles | **Mis comentarios:** Delicia vs delina | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 46 | Lastenia Barrero | — | — (el premio no tiene objeto en el catálogo) | **Coment LM:** ¿qué debería mirar acá? | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 48 | Isaura Sorroza de Risso Patron | 3 | Isaura S. de Risso Patrón | **Coment LM:** ok | observación / confirmación |
| 60 | Argenia R. de Lautafy | 170 | Rosalía Gutiérrez | **Mis comentarios:** DE + apellido / **Coment LM:** ok | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 62 | Mercedes Pereyra | 174 | María M. Pereira | **Mis comentarios:** No hay una Pereyra en el catalogo | observación / confirmación |
| 64 | Adela Amuchástegui | 180 | María S. Amuchástegui | **Mis comentarios:** No parecen ser la misma. Pero no hay una Adela | observación / confirmación |
| 73 | Elvira Rodríguez | 90 | Elvira Rodríguez They | **Mis comentarios:** Segundo apellido | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
| 80 | Alejandrina Peiró | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No está Alejandrina en el catálogo | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 86 | Lucrecia Carrazan | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No hay una Lucrecia Sarrazan en el catalogo | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 87 | Ezequiela P. de Gutiérrez | 195 | Esequiela P. de Gutiérrez | **Mis comentarios:** Esequiela vs Ezequiela / **Coment LM:** dejaría Ezequiela | PENDIENTE: LM pide 'Ezequiela'; la expositora sigue como 'Esequiela' |
| 89 | Amicia Diaz | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No hay una Amicia Díaz en el catalogo | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 103 | Catalina de Figueroa | 110 | Catalina R. de Figueroa | **Mis comentarios:** R. / **Coment LM:** ok | observación de forma del nombre — comparar contra 'Nombre real' y decidir |
