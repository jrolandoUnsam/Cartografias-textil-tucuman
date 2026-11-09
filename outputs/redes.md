# Redes de participación

Generado por `src/pipeline/12_redes.py` en cada corrida. Las aristas de apellido son **hipótesis de parentesco**, no datos: sirven para orientar la búsqueda en otras fuentes. El grafo completo está en `data/processed/redes.xlsx`.

## Resumen

- 458 registros de expositoras (8 instituciones), 68 lugares, 15 integrantes de comisión.
- **32 expositoras expusieron en los dos concursos** (7 % de los registros).
- 198 pares con apellido en común en el mismo lugar, que forman 61 grupos (41 con algún apellido poco frecuente). De esos pares, 68 combinan apellido propio con apellido de casada (¿madre e hija, suegra y nuera?).
- 5 coincidencias de apellido entre la comisión y las expositoras.

## Expositoras que repitieron (1915 y 1916)

| Nombre | Lugar | Obras | Premios |
|---|---|---|---|
| Concepción y Rosa Cuello | San José de Piedra Blanca | 36 | 5 |
| Escuela y Hogar de Obreras de la Sociedad de Beneficencia | San Miguel de Tucumán | 14 | 1 |
| Edelmira C. de Roldán | San Miguel de Tucumán | 8 | 2 |
| Dalmira González Sorol | San Miguel de Tucumán; Tafí Viejo | 7 | 2 |
| Enriqueta Fronzuti | San Miguel de Tucumán | 7 | 1 |
| Rosa Alderete | Monteros | 7 | 1 |
| Isabel B. de Acuña de Zavalía | San Miguel de Tucumán | 6 | 2 |
| María J. de Aguirre | San Miguel de Tucumán | 5 | 0 |
| Rosario Gramajo | Monteagudo | 5 | 1 |
| Alfonsa [Cuadrado] de Barceló | San Miguel de Tucumán | 4 | 1 |
| Irene C. de Aybar | San Miguel de Tucumán | 4 | 2 |
| Rosa Baralo | San Miguel de Tucumán | 4 | 0 |
| Sara M. Sal | San Miguel de Tucumán | 4 | 1 |
| Ángeles Cuadrados | San Miguel de Tucumán | 4 | 2 |
| Ana de Tactagi | San Miguel de Tucumán | 3 | 1 |
| Corina Aguirre | San Miguel de Tucumán | 3 | 1 |
| Facunda Cerone [Coronel] | La Cocha | 3 | 1 |
| Hermanas dominicas [asilo] | San Miguel de Tucumán | 3 | 2 |
| Isaura Sorroza de Risso Patrón | Monteros | 3 | 1 |
| Leticia Sorroza | Monteros | 3 | 1 |
| Lorenza V. de Panei [Pérez] | San Miguel de Tucumán | 3 | 1 |
| Mercedes del Moral | Monteros; San Miguel de Tucumán | 3 | 0 |
| Palmira Contreras | Santiago del Estero (solo provincia) | 3 | 1 |
| Rosa V. [de] Lescano | Santiago del Estero (solo provincia) | 3 | 1 |
| Dolores Galván | Monteros | 2 | 1 |
| Dominga Villoldo | San Miguel de Tucumán; San Pablo | 2 | 1 |
| Elisa Blanche | San Miguel de Tucumán | 2 | 1 |
| Hortensia Haurigot | San Miguel de Tucumán | 2 | 1 |
| Juana Pérez | San Miguel de Tucumán | 2 | 1 |
| Lastenia Barrero | San Miguel de Tucumán | 2 | 1 |
| Mamerta Monteros [Escuela Sarmiento 1915] | San Miguel de Tucumán | 2 | 1 |
| María Cleofé de Bustamante | Simoca; Yacuchiri | 2 | 1 |

## Lugares

Expositoras distintas por lugar y cuántas de ellas expusieron en los dos concursos.

| Nombre | Provincia | Expositoras | Repiten | Obras |
|---|---|---|---|---|
| San Miguel de Tucumán | Tucumán | 167 | 22 | 359 |
| Chicligasta | Tucumán | 35 | 0 | 52 |
| Monteros | Tucumán | 28 | 5 | 48 |
| Catamarca (solo provincia) | Catamarca | 27 | 0 | 59 |
| Santiago del Estero (solo provincia) | Santiago del Estero | 17 | 2 | 47 |
| Monteagudo | Tucumán | 16 | 1 | 29 |
| Atahona | Tucumán | 15 | 0 | 19 |
| Niogasta | Tucumán | 14 | 0 | 17 |
| Orán |  | 13 | 0 | 24 |
| La Cocha | Tucumán | 12 | 1 | 21 |
| Graneros | Tucumán | 8 | 0 | 12 |
| Concepción | Tucumán | 7 | 0 | 15 |
| Colalao del Valle | Tucumán | 6 | 0 | 30 |
| Los Sandovales | Tucumán | 6 | 0 | 9 |
| Simoca | Tucumán | 6 | 1 | 7 |
| Banda del Río Salí | Tucumán | 5 | 0 | 19 |
| Las Lechuzas | Tucumán | 5 | 0 | 8 |
| La Ensenada | Tucumán | 5 | 0 | 7 |
| San Pablo | Tucumán | 4 | 1 | 14 |
| San Pedro de Colalao | Tucumán | 4 | 0 | 8 |

## Grupos por apellido y lugar (hipótesis)

Componentes conexas de la arista `mismo_apellido`. Confianza baja = todos los apellidos del grupo los llevan 5 o más registros.

| Personas | Apellidos | Lugar | Confianza | Integrantes |
|---|---|---|---|---|
| 9 | González | Chicligasta | baja | Cenobia González; Demofila González; Gabriel González; Indamira González; José Tobías González; Lola González; Lugarda [Lujarda] J. de González; Rita González; Sofía C. de González |
| 7 | Gramajo | Monteagudo, Niogasta | baja | Adela G. de Gramajo; Adela J. de Gramajo; Cruz Gramajo; Elena Gramajo; Eleuterio Gramajo; Manuela Gramajo; Rosario Gramajo |
| 7 | Robles | Monteros, Orán | baja | Delina [Delicia] G. de Robles; Liboria Robles; M. Amelia Robles; Margarita T. Robles; María Luisa Robles; Patricia de Robles; Ángela Robles |
| 5 | Aguilar | Niogasta | baja | Alcira Aguilar; Bartolina Aguilar; Carmen Aguilar; Jacoba Aguilar; Justa E. de Aguilar |
| 5 | Herrera | Chicligasta | baja | Candelaria Herrera; Gregoria L. de Herrera; Rosario Herrera; Rosario del Carmen Herrera; Salvadora de Herrera |
| 5 | Pérez | La Ensenada | baja | Mamerta Pérez; María Pérez; Mercedes Pérez; Ramona de Pérez; Valentina Pérez |
| 5 | Sal | San Miguel de Tucumán | baja | Argentina J. Sal; Carmen Sal; Dalmira C. de Sal; Elvira Sal; Sara M. Sal |
| 4 | Belmonte | San Miguel de Tucumán | media | Concepción Belmonte; Consuelo Belmonte; Marina Belmonte; Máxima Belmonte |
| 4 | Luna | Chicligasta | baja | Laurentina Luna; María Luna; Rosario Luna; Salvadora Luna |
| 3 | Acosta | San Miguel de Tucumán | media | Esther Acosta; Francisca de Acosta; María Cruz Acosta |
| 3 | Aguirre | San Miguel de Tucumán | baja | Angélica Aguirre; Corina Aguirre; María J. de Aguirre |
| 3 | Alderete | Monteros | media | Aurora Alderete; Bartolina Alderete; Rosa Alderete |
| 3 | Bazán | San Miguel de Tucumán | media | Antonia Díaz Bazán; Carmela Bravo Bazán; María Díaz y Victoria Bazán |
| 3 | Díaz | Atahona | baja | Asunción Díaz; Lorenza de Díaz; Romelia M. de Díaz |
| 3 | Espinosa | Niogasta | media | Delia Espinosa; Delina R. Espinosa; Simona Espinosa |
| 3 | Fernández | Concepción | baja | Arsenia Fernández; Lidia Fernández; María Fernández |
| 3 | Lescano | Chicligasta | baja | Lola Lescano; Lorenza Lescano; Mercedes Lescano |
| 3 | Llaví, Puig | San Miguel de Tucumán | media | María Llaví de Puig; María Slopart de Llaví; Sra. de Puig |
| 3 | López | San Miguel de Tucumán | baja | Carmen López; Hortensia D. de López; Rosa López |
| 3 | Paz | Orán | media | Aurelia Paz; Josefa Robles Paz; Rosa Paz |
| 3 | Pereira | San Miguel de Tucumán | media | Carmen Pereira; María Elvira Pereira; María Mercedes Pereira |
| 3 | Pérez | Atahona | baja | Carmen Pérez; Concepción de Pérez; María T. de Pérez |
| 3 | Segura | Banda del Río Salí | media | Angélica Segura; Felipa L. de Segura; Rosario Segura |
| 3 | Villoldo | San Miguel de Tucumán | baja | Dominga Villoldo; Francisca Villoldo; Rafaela Villoldo |
| 2 | Aguirre | Río Chico | baja | Julia Aguirre; Rosario Aguirre |
| 2 | Alarcón | Atahona | media | Genuaria Alarcón; Paulina M. de Alarcón |
| 2 | Albaca | San Miguel de Tucumán | media | Enriqueta Albaca; María de Albaca |
| 2 | Alincastro | Orán | media | Candelaria Alincastro; Florinda Q. de Alincastro |
| 2 | Ariza | Monteros | media | Rita Ariza; Rosa Ariza |
| 2 | Blanche | San Miguel de Tucumán | media | Elisa Blanche; Juana Blanche |

## Comisión y expositoras con apellido en común (hipótesis)

| Comisión | Expositora | Apellido |
|---|---|---|
| María Helguera de Frías | Tomasa Frías | Frías |
| Sofía Colombres de Colombres | Arminda de Colombres | Colombres |
| Sofía Colombres de Colombres | Juana Rosa Lanza Colombres | Colombres |
| Victoria Haurigot | Hortensia Haurigot | Haurigot |
| Salomé Cordero de Molina | Ercilia Gallo Molina | Molina |
