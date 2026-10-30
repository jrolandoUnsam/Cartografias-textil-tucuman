# Auditoría de comentarios — estado de aplicación

_Generado por `src/pipeline/audit_comentarios.py` — no editar a mano._

Compara cada decisión anotada a mano contra el estado actual de `data/processed/tabla_normalizada.xlsx`, tomando como línea de base `data/interim/tabla_normalizada_manual.xlsx` (la tabla antes del pipeline).

**Hallazgo global:** respecto de la tabla de partida (`tabla_normalizada_manual.xlsx`) se reasignaron **84 objetos** y desaparecieron **61 filas** de `Expositoras`: las fusiones **sí** están aplicadas. Nombres normalizados: 31.

**Veredictos:**
- `SIN HACER` — la fila sigue igual que en la línea de base.
- `SOLO NOMBRE` — se corrigió/normalizó el nombre, pero las dos filas **siguen sin fusionar** (los objetos no se movieron).
- `SOLO NOMBRE · OBJETOS PARTIDOS` — ídem, y además hay objetos en la fila que el comentario manda descartar → fusionar no es solo borrar.
- `FUSIÓN OK` — una fila desapareció y quedó la que pide el comentario.
- `FUSIÓN REVISAR` — una fila desapareció pero quedó la otra.
- `OK SEPARAR` — se pidió **no** unificar y siguen las dos filas (correcto).
- `CONTRA LO PEDIDO` — se pidió separar y se fusionó, o al revés.
- `FUSIÓN OK (en un tercer id)` — las dos filas desaparecieron porque entraron en un grupo de 3 o más; sus objetos están juntos en otro id.
- `DUDA ABIERTA` — el comentario sólo pregunta; no hay decisión que verificar.

## 1. `revision_duplicados.xlsx` — hoja *Personas - candidatos*

_Conteo:_ DUDA ABIERTA: 3 · FUSIÓN OK: 51 · FUSIÓN OK (en un tercer id): 8 · OK SEPARAR: 7

| # | id A / nombre | id B / nombre | Hecho | Comentario | Decisión leída | Estado actual | Veredicto |
|---|---|---|---|---|---|---|---|
| 1 | `126` Gregoria Luna | `269` — | True | son la misma | Unificar (cualquiera de las dos) | 1 fila: 126 (Gregoria Luna) · 10 obj | **FUSIÓN OK** |
| 2 | `223` Elisa B. de Gramajo | `408` — | True | son la misma | Unificar (cualquiera de las dos) | 1 fila: 223 (Elisa B. de Gramajo) · 2 obj | **FUSIÓN OK** |
| 3 | `244` Edelmira A. de Moreno | `279` — | True | son la misma | Unificar (cualquiera de las dos) | 1 fila: 244 (Edelmira A. de Moreno) · 10 obj | **FUSIÓN OK** |
| 4 | `16` — | `426` Palmira Contreras | True | dejamos b | Unificar → conservar B (426) | 1 fila: 426 (Palmira Contreras) · 3 obj | **FUSIÓN OK** |
| 5 | `40` — | `461` Enriqueta Fronzuti | True | dejamos b | Unificar → conservar B (461) | 1 fila: 461 (Enriqueta Fronzuti) · 7 obj | **FUSIÓN OK** |
| 6 | `82` Ángeles Cuadrados | `514` — | True | dejamos a | Unificar → conservar A (82) | 1 fila: 82 (Ángeles Cuadrados) · 4 obj | **FUSIÓN OK** |
| 7 | `25` Concepción y Rosa Cuello | `282` — | True | son la misma, dejamos con tilde | Unificar → conservar A (25) | 1 fila: 25 (Concepción y Rosa Cuello) · 36 obj | **FUSIÓN OK** |
| 8 | `35` María J. de Aguirre | `373` — | False | J o I? Visto en fotos / lo unifiqué con la J. no vi el I, ¿sería del catálogo? | Unificar (cualquiera de las dos) | 1 fila: 35 (María J. de Aguirre) · 5 obj | **FUSIÓN OK** |
| 9 | `59` — | `252` Lorenza V. de Panei [Pérez] | False | unificamos panei para que se identifique que es la misma y porque es apellido más común, pero dejaremos registro de la elección | Unificar (cualquiera de las dos) | 1 fila: 252 (Lorenza V. de Panei [Pérez]) · 3 obj | **FUSIÓN OK** |
| 10 | `102` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | `117` — | True | Escuela y Hogar de Obreras de la Sociedad de Beneficencia | Unificar (cualquiera de las dos) | 1 fila: 102 (Escuela y Hogar de Obreras de la Sociedad de Beneficencia) · 14 obj | **FUSIÓN OK** |
| 11 | `121` Tránsito Soaje de Ree | `381` — | True | dejamos con tilde | Unificar → conservar A (121) | 1 fila: 121 (Tránsito Soaje de Ree) · 5 obj | **FUSIÓN OK** |
| 12 | `196` Concepción de Pérez | `319` — | True | dejamos con tilde | Unificar (cualquiera de las dos) | 1 fila: 196 (Concepción de Pérez) · 3 obj | **FUSIÓN OK** |
| 13 | `270` Felisa R. de Sánchez | `278` — | True | dejamos con tilde | Unificar → conservar A (270) | 1 fila: 270 (Felisa R. de Sánchez) · 9 obj | **FUSIÓN OK** |
| 14 | `286` — | `492` Superiora del Colegio Santa Rosa de Viterbo | True | dejamos b | Unificar → conservar B (492) | 1 fila: 492 (Superiora del Colegio Santa Rosa de Viterbo) · 2 obj | **FUSIÓN OK** |
| 15 | `313` — | `319` — | True | dejamos con tilde | Unificar → conservar B (319) | las dos fusionadas en `196` (Concepción de Pérez) · 3 obj | **FUSIÓN OK (en un tercer id)** |
| 16 | `329` — | `345` María Slopart de Llaví | True | dejamos con tilde | Unificar → conservar B (345) | 1 fila: 345 (María Slopart de Llaví) · 2 obj | **FUSIÓN OK** |
| 17 | `3` Isaura Sorroza de Risso Patrón | `442` — | True | dejamos A | Unificar → conservar A (3) | 1 fila: 3 (Isaura Sorroza de Risso Patrón) · 3 obj | **FUSIÓN OK** |
| 18 | `12` — | `120` Lastenia Barrero | False | Dejamos barrero, fue una figura importante | Unificar → conservar B (120) | 1 fila: 120 (Lastenia Barrero) · 2 obj | **FUSIÓN OK** |
| 19 | `70` María Cleofé de Bustamante | `213` — | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (70) | 1 fila: 70 (María Cleofé de Bustamante) · 2 obj | **FUSIÓN OK** |
| 20 | `117` — | `450` — | True | Escuela y Hogar de Obreras de la Sociedad de Beneficencia (ídem arriba) | Unificar (cualquiera de las dos) | las dos fusionadas en `102` (Escuela y Hogar de Obreras de la Sociedad de Beneficencia) · 14 obj | **FUSIÓN OK (en un tercer id)** |
| 21 | `139` — | `261` — | True | dejamos con tilde | Unificar → conservar B (261) | las dos fusionadas en `52` (Edelmira C. de Roldán) · 8 obj | **FUSIÓN OK (en un tercer id)** |
| 22 | `161` Delina J. de Román | `209` Delina J. de Román | False | MUY POLÉMICO. este no lo unificaría, no queda claro si son la misma persona o un familiar que podía prestarle lana de vicuña para tejer. total al momento de buscar info de vicuña se verá el matiz. por ahora lo dejaría así hasta más info a futuro- | Mantener SEPARADAS | 2 filas · A:1 obj, B:2 obj | **OK SEPARAR** |
| 23 | `161` Delina J. de Román | `264` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Duda (sin decisión) | 2 filas · A:1 obj, B:3 obj | **DUDA ABIERTA** |
| 24 | `209` Delina J. de Román | `255` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Duda (sin decisión) | 2 filas · A:2 obj, B:1 obj | **DUDA ABIERTA** |
| 25 | `255` Delina I. de Román | `264` Delina I. de Román | False | J o I? Además, aparece en 3 ciudades distintas: Belén, Ciudad y Catamarca | Duda (sin decisión) | 2 filas · A:1 obj, B:3 obj | **DUDA ABIERTA** |
| 26 | `8` — | `87` Isabel del Río | True | dejamos con tilde | Unificar → conservar B (87) | 1 fila: 87 (Isabel del Río) · 2 obj | **FUSIÓN OK** |
| 27 | `165` — | `297` Lorenza de Díaz | True | dejamos con tilde | Unificar → conservar B (297) | 1 fila: 297 (Lorenza de Díaz) · 2 obj | **FUSIÓN OK** |
| 28 | `187` — | `301` Lugarda Juárez | True | dejamos con tilde | Unificar → conservar B (301) | 1 fila: 301 (Lugarda Juárez) · 2 obj | **FUSIÓN OK** |
| 29 | `194` Ramona de Pérez | `312` — | True | dejamos con tilde | Unificar → conservar A (194) | 1 fila: 194 (Ramona de Pérez) · 2 obj | **FUSIÓN OK** |
| 30 | `221` Segunda Giménez | `268` Segunda Jiménez | False | De momento no las uniría (la vicuña es una práctica tan específica que me da duda, no son dos vicuñas las que mandó) | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 31 | `19` Mercedes del Moral | `441` Mercedes G. del Moral | False | Aparece como de San Miguel 1915 y de Monteros 1916 /lo mantendría como está | Mantener SEPARADAS | 2 filas · A:3 obj, B:1 obj | **OK SEPARAR** |
| 32 | `52` Edelmira C. de Roldán | `261` — | True | dejamos el A | Unificar → conservar A (52) | 1 fila: 52 (Edelmira C. de Roldán) · 8 obj | **FUSIÓN OK** |
| 33 | `148` — | `256` María Salinas | True | dejamos con tilde | Unificar → conservar B (256) | 1 fila: 256 (María Salinas) · 4 obj | **FUSIÓN OK** |
| 34 | `191` — | `302` María A. de Argañaraz | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar B (302) | 1 fila: 302 (María A. de Argañaraz) · 2 obj | **FUSIÓN OK** |
| 35 | `220` Dorotea C. de Lazarte | `308` — | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (220) | 1 fila: 220 (Dorotea C. de Lazarte) · 3 obj | **FUSIÓN OK** |
| 36 | `231` Rita González | `290` — | True | dejamos con tilde | Unificar → conservar A (231) | 1 fila: 231 (Rita González) · 2 obj | **FUSIÓN OK** |
| 37 | `7` — | `32` Ana del Río | True | dejamos con tilde | Unificar → conservar B (32) | 1 fila: 32 (Ana del Río) · 2 obj | **FUSIÓN OK** |
| 38 | `86` Juana Pérez | `465` — | True | dejamos con tilde | Unificar → conservar A (86) | 1 fila: 86 (Juana Pérez) · 2 obj | **FUSIÓN OK** |
| 39 | `115` María Ávila | `222` — | True | dejamos con tilde | Unificar → conservar A (115) | 1 fila: 115 (María Ávila) · 20 obj | **FUSIÓN OK** |
| 40 | `118` — | `271` — | True | dejamos b | Unificar → conservar B (271) | las dos fusionadas en `281` (Escuela Profesional de Mujeres) · 26 obj | **FUSIÓN OK (en un tercer id)** |
| 41 | `152` — | `323` Mercedes Ruiz de Arzuaga | True | dejamos el b | Unificar → conservar B (323) | 1 fila: 323 (Mercedes Ruiz de Arzuaga) · 2 obj | **FUSIÓN OK** |
| 42 | `159` — | `308` — | True | ídem arriba | Unificar (cualquiera de las dos) | las dos fusionadas en `220` (Dorotea C. de Lazarte) · 3 obj | **FUSIÓN OK (en un tercer id)** |
| 43 | `219` Amelia N. de Plaza | `285` — | True | dejamos a | Unificar → conservar A (219) | 1 fila: 219 (Amelia N. de Plaza) · 3 obj | **FUSIÓN OK** |
| 44 | `260` — | `283` María Rueda | True | dejamos con tilde | Unificar → conservar B (283) | 1 fila: 283 (María Rueda) · 4 obj | **FUSIÓN OK** |
| 45 | `373` — | `407` — | True | unifiqué porque ambos envíos además son irlansa | Unificar (cualquiera de las dos) | las dos fusionadas en `35` (María J. de Aguirre) · 5 obj | **FUSIÓN OK (en un tercer id)** |
| 46 | `54` — | `284` Irene C. de Aybar | True | dejamos b | Unificar → conservar B (284) | 1 fila: 284 (Irene C. de Aybar) · 4 obj | **FUSIÓN OK** |
| 47 | `67` — | `76` Arsenia F. Medina | True | Vamos con Arsenia F. Medina. Veo que no está en el listado, falta la 67, ¿será que hice lío? | Unificar (cualquiera de las dos) | 1 fila: 76 (Arsenia F. Medina) · 2 obj | **FUSIÓN OK** |
| 48 | `295` María Luna | `309` — | True | dejamos con tilde | Unificar → conservar A (295) | 1 fila: 295 (María Luna) · 2 obj | **FUSIÓN OK** |
| 49 | `78` Antonia de Soria | `101` — | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (78) | 1 fila: 78 (Antonia de Soria) · 4 obj | **FUSIÓN OK** |
| 50 | `385` — | `400` M. Luisa Roberti | True | dejamos b | Unificar → conservar B (400) | 1 fila: 400 (M. Luisa Roberti) · 2 obj | **FUSIÓN OK** |
| 51 | `102` Escuela y Hogar de Obreras de la Sociedad de Beneficencia | `450` — | True | Dejar completo: Escuela y Hogar de Obreras de la Sociedad de Beneficencia | Unificar (cualquiera de las dos) | 1 fila: 102 (Escuela y Hogar de Obreras de la Sociedad de Beneficencia) · 14 obj | **FUSIÓN OK** |
| 52 | `161` Delina J. de Román | `255` Delina I. de Román | True | ídem arriba, las dejaría separadas de momento | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 53 | `196` Concepción de Pérez | `313` — | True | dejamos con tilde | Unificar → conservar A (196) | 1 fila: 196 (Concepción de Pérez) · 3 obj | **FUSIÓN OK** |
| 54 | `348` — | `466` Julia M. Chirou | True | dejamos b | Unificar → conservar B (466) | 1 fila: 466 (Julia M. Chirou) · 3 obj | **FUSIÓN OK** |
| 55 | `364` Asilo del Buen Pastor | `521` — | False | DEL /dejamos del | Unificar → conservar A (364) | 1 fila: 364 (Asilo del Buen Pastor) · 6 obj | **FUSIÓN OK** |
| 56 | `31` — | `55` Ana de Tactagi | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar B (55) | 1 fila: 55 (Ana de Tactagi) · 3 obj | **FUSIÓN OK** |
| 57 | `162` Carmen de Moya | `296` — | False | DE /en los casos en que es DE mantenerlo (aporta más info) | Unificar → conservar A (162) | 1 fila: 162 (Carmen de Moya) · 10 obj | **FUSIÓN OK** |
| 58 | `182` Delina R. Espinosa | `183` Delia Espinosa | True | estas no son la misma, quizás familia porque la tercera en el catálogo es simona espinosa | Mantener SEPARADAS | 2 filas · A:1 obj, B:3 obj | **OK SEPARAR** |
| 59 | `289` — | `470` — | True | dejamos con tilde, lo unificaría con el de abajo 234, 289, 470 | Unificar → conservar A (289) | las dos fusionadas en `234` (Sofía C. de González) · 5 obj | **FUSIÓN OK (en un tercer id)** |
| 60 | `333` Margarita García de Esparré | `354` — | True | dejamos a | Unificar → conservar A (333) | 1 fila: 333 (Margarita García de Esparré) · 3 obj | **FUSIÓN OK** |
| 61 | `52` Edelmira C. de Roldán | `139` — | True | Dejamos el que aporta más info A | Unificar → conservar A (52) | 1 fila: 52 (Edelmira C. de Roldán) · 8 obj | **FUSIÓN OK** |
| 62 | `381` — | `389` — | True | Dejar el que aporta más info A | Unificar → conservar A (381) | las dos fusionadas en `121` (Tránsito Soaje de Ree) · 5 obj | **FUSIÓN OK (en un tercer id)** |
| 63 | `23` Rosa Alderete | `422` Aurora Alderete | False | Ambas de Montero categoria Randas. Madre e Hija? /ojalá! es para un estudio a futuro hablar con las randeras. Por ahora el único apellido que aparece publicado en una genealogía con randeras es Lorenza Alderete de Núñez. | Mantener SEPARADAS | 2 filas · A:7 obj, B:1 obj | **OK SEPARAR** |
| 64 | `92` Carmen Pereira | `201` Carmen Herrera | True | estos no son el mismo nombre, están unidos por algo en particular? | Mantener SEPARADAS | 2 filas · A:1 obj, B:1 obj | **OK SEPARAR** |
| 65 | `234` Sofía C. de González | `289` — | False | unifiqué con el más completo | Unificar (cualquiera de las dos) | 1 fila: 234 (Sofía C. de González) · 5 obj | **FUSIÓN OK** |
| 66 | `234` Sofía C. de González | `470` — | False | unifiqué con el más completo | Unificar (cualquiera de las dos) | 1 fila: 234 (Sofía C. de González) · 5 obj | **FUSIÓN OK** |
| 67 | `409` María Abigail Gómez | `460` — | True | Dejar A | Unificar → conservar A (409) | 1 fila: 409 (María Abigail Gómez) · 5 obj | **FUSIÓN OK** |
| 68 | `4` Dalmira González Sorol | `404` — | False | Tafi Viejo en 1915 y Tucumán 1916 /dejaría cada ciudad como está | Unificar (la ciudad queda en cada objeto) | 1 fila: 4 (Dalmira González Sorol) · 7 obj | **FUSIÓN OK** |
| 69 | `28` — | `110` Rosario B. D'Empaire | False | vamos con B | Unificar → conservar B (110) | 1 fila: 110 (Rosario B. D'Empaire) · 3 obj | **FUSIÓN OK** |

## 2. `revision_duplicados.xlsx` — hoja *Ciudades - candidatos*

| # | id A / nombre | id B / nombre | Hecho | Comentario | Estado actual | Veredicto |
|---|---|---|---|---|---|---|
| 1 | `26` ASILO CIUDAD | `79` ASILO, CIUDAD | False | — | 2 filas · A:6 obj, B:1 obj | **OK SEPARAR** |
| 2 | `37` LAMADRID | `52` LA MADRID | True | La  Madrid | 1 fila: 52 (La Madrid) | **FUSIÓN OK** |
| 3 | `62` GUCHEA | `80` GUCHEAS | True | Gucheas | 1 fila: 80 (Gucheas) | **FUSIÓN OK** |
| 4 | `9` CÓRDOBA | `63` CORDOBA | True | — | 1 fila: 9 (Córdoba) | **FUSIÓN OK** |

## 3. `tabla_normalizada.xlsx` — hoja *Premios* (filas con comentario)

> Las 8 columnas originales de la hoja Premios están **intactas** respecto de la tabla de partida (sin contar espacios de más). El vínculo que se muestra es el de la hoja curada de `04e_premios.py`.
>
> Los comentarios de esta hoja son **observaciones sobre nombres**, no órdenes de fusión. La columna *Nombre real de la expositora* muestra a quién apunta hoy el `objeto_id` de esa fila (vía `Objetos.expositora_id`).

| premio_id | NOMBRE en el fallo | objeto_id | Nombre real de la expositora (hoy) | Comentario(s) | Estado |
|---|---|---|---|---|---|
| 0 | Angela L. de Diblasi | 108 | Ángela S. [L.] de Diblasi | **Mis comentarios:** Angela L. vs Angela S | observación sin respuesta de LM |
| 6 | Dominga Castaño | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Son distintas personas para mi / **Coment LM:** Sí, son distintas. En el doc. de premiación figura "fuera de catálogo" probablemente por eso. | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 8 | Vicenta B. de Medina | 121 | Vicenta V. [B.] de Medina | **Mis comentarios:** Vicenta V. vs Vicenta B. / **Coment LM:** ¿Te parece poner Vicenta V. [B.] de Medina? Así dejamos entre corchetes la otra referencia con la que se refiere a la misma persona. Siendo entre corchetes la versión de la premiación. | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 10 | Maria C. Bustamante | 122 | María Cleofé de Bustamante | **Mis comentarios:** Encontramos segundo nombre / **Coment LM:** buenísimo | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 13 | Lorenza V. de Pérez | 107 | Lorenza V. de Panei [Pérez] | **Mis comentarios:** Parece ser la misma persona. Vista en catalogo como de Panci y Panei / **Coment LM:** ídem 10. Lorenza V. de Panei [Pérez] | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 14 | Rosa V. de Lescano | 103 | Rosa V. [de] Lescano | **Mis comentarios:** Lescano vs Lezcano. Nuevo posible duplicado no visto antes / **Coment LM:** vamos con Lescano (así aparece el apellido la mayoría de las veces) | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 15 | Lujarda J. de González | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda / **Coment LM:** Ídem acá también aparece en la premiación como "fuera de catálogo". Lugarda [Lujarda] J. de González | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 16 | Lujarda J Gonzalez | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda. Además, es raro porque parece que ganan dos mujeres distintas según las fotos de los premios, una es de Gonzalez y la otra González. | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 18 | Melchora Valenzuela | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** el número de orden citado no existe en esa categoría del catálogo / **Coment LM:** acá no sé si tendría que ver algo | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 19 | Catalina Figueroa | 110 | Catalina R. de Figueroa | **Coment LM:** ídem arriba | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 20 | Isabel B. de Acuña de Zavalia | 145 | Isabel B. de Acuña de Zavalía | **Mis comentarios:** DE Zavalia y tilde en i / **Coment LM:** Perfecto, lo dejamos en su versión más completa. Mantengamos las tildes. | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 21 | (Sra.) de Plaza | 140 | Sra. de Plaza | **Mis comentarios:** Sra / **Coment LM:** logré ver lo mismo en el catálogo, genial, ok con sra! | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 24 | Elvira Araoz | 98 | Eloisa [Elvira] Aráoz | **Coment LM:** Dejamos Eloisa [Elvira] Aráoz | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 25 | Delia Ruiz | 97 | Delicia [Delia] Ruiz | **Coment LM:** Dejamos Delicia [Delia] Ruiz | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 28 | Escuela y hogar de obreras de la sociedad de beneficencia | 192 | Escuela y Hogar de Obreras de la Sociedad de Beneficencia | **Mis comentarios:** Misma / **Coment LM:** ok | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 31 | Clemencia Zelarayan | 193 | Clemencia Zelarayán | **Mis comentarios:** DE + apellido / **Coment LM:** ok | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 35 | Rosa Valenzuela | 135 | Rosa V. de Valenzuela | **Mis comentarios:** V. Aparentemente apellido o segundo nombre / **Coment LM:** ok | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 36 | Arsenia Medina | 134 | Arsenia F. Medina | **Mis comentarios:** F. Aparentemente apellido o segundo nombre / **Coment LM:** ok | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 39 | Lujarda J. de González | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** Lugarda vs Lujarda / **Coment LM:** Lugarda [Lujarda] J. de González | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 41 | Dominga Lezcano | 43 | Dominga Lescano | **Mis comentarios:** Lescano vs Lezcano / **Coment LM:** vamos con Lescano (así aparece el apellido la mayoría de las veces) | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 43 | Delicia G. de Robles | 34 | Delina [Delicia] G. de Robles | **Mis comentarios:** Delicia vs delina / **Coment LM:** Delina [Delicia] G. de Robles | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 46 | Lastenia Barrero | 17 | Lastenia Barrero | **Mis comentarios:** No hay orden 19. / **Coment LM:** ¿qué debería mirar acá? | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 48 | Isaura Sorroza de Risso Patron | 3 | Isaura Sorroza de Risso Patrón | **Coment LM:** ok el más completo | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 50 | Maria Castillejo | 55 | María Castillón [Castillejo] | **Coment LM:** María Castillón [Castillejo] | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 60 | Argenia R. de Lautafy | 59 | Argenia R. de Lautafy | **Mis comentarios:** DE + apellido / **Coment LM:** ok dejamos el más completo | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 62 | Mercedes Pereyra | 174 | María Mercedes Pereira | **Mis comentarios:** No hay una Pereyra en el catalogo / **Coment LM:** En el catálogo coincide con el envío n.17 de crochet, traje punto irlanda. MARÍA M. PEREIRA (que debe ser María Mercedes). Lo podemos unificar como María Mercedes Pereira. | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 64 | Adela Amuchástegui | 180 | María S. [Adela] Amuchástegui | **Mis comentarios:** No parecen ser la misma. Pero no hay una Adela / **Coment LM:** María S. [Adela] Amuchástegui | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 67 | Hermanas domínicas | — | — (el premio no tiene objeto en el catálogo) | **Coment LM:** sin tilde | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 71 | Argentina Sal | 83 | Argentina J. Sal | **Coment LM:** ok el más completo | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 73 | Elvira Rodríguez | 90 | Elvira Rodríguez They | **Mis comentarios:** Segundo apellido / **Coment LM:** perfect | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 80 | Alejandrina Peiró | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No está Alejandrina en el catálogo / **Coment LM:** está bien, debe haber sido fuera de catálogo. La dejamos suelta | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 82 | Sta Santés | 94 | Sta. Sandés | **Mis comentarios:** solo llega a 13 (la observación dice "sección deshilados" — ahí sí llega hasta 25, quizás haya que buscarlo ahí en vez de en Bordado) / **Coment LM:** Excelente. Además se identifica Santiago con Santiago del Estero del Catálogo. Nos viene re bien. | respondida por LM — el nombre que quedó está en 'Nombre real' |
| 86 | Lucrecia Carrazan | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No hay una Lucrecia Carrazan en el catalogo / **Coment LM:** la dejamos suelta como alejandrina | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 87 | Ezequiela P. de Gutiérrez | 195 | Ezequiela P. de Gutiérrez | **Mis comentarios:** Esequiela vs Ezequiela / **Coment LM:** dejaría Ezequiela | resuelto: la expositora ya figura como 'Ezequiela' |
| 89 | Amicia Diaz | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** No hay una Amicia Díaz en el catalogo / **Coment LM:** la dejamos suelta como alejandrina | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
| 103 | Catalina de Figueroa | — | — (el premio no tiene objeto en el catálogo) | **Mis comentarios:** R. / **Coment LM:** ok | decisión: sin objeto en el catálogo (queda como nota, sin lugar formal aún) |
