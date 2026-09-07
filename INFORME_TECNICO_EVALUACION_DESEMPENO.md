# Rediseño del proceso de evaluación y calificación del desempeño académico en la Facultad de Ingeniería, Universidad de Santiago de Chile: diagnóstico, propuesta normativa y prototipo de sistema piloto (agosto–septiembre de 2026)

**Informe técnico-académico**

**Institución:** Facultad de Ingeniería, Universidad de Santiago de Chile (FING-USACH)
**Período cubierto:** agosto 2026 – 7 de septiembre de 2026
**Repositorio:** `anibalroman-ops/Dise-o`, rama `claude/inkscape-automation-scripts-3nrjdj`
**Elaborado por:** asistencia técnica Claude Code, a partir del historial de trabajo, la documentación normativa y la evidencia empírica del proyecto

---

## Resumen

Este informe documenta, con estructura IMRaD, el proceso de diagnóstico, rediseño normativo y desarrollo de un sistema piloto para la evaluación y calificación del desempeño académico en la Facultad de Ingeniería de la Universidad de Santiago de Chile (FING-USACH), ejecutado entre agosto y septiembre de 2026. El proyecto combinó métodos cualitativos (análisis temático de cuatro entrevistas semiestructuradas, según Braun y Clarke, 2006) y cuantitativos (consulta a 55 académicos de diez unidades, con análisis de clúster de la carga académica declarada) para caracterizar el proceso vigente, encontrando que ninguna de sus seis dimensiones evaluadas alcanza una media de 3,0 en una escala de 1 a 4, con una tensión central en la gobernanza (63,6 % de menciones cualitativas) y en el reconocimiento de perfiles y trayectorias diferenciadas (media 2,15; peor dimensión evaluada). A partir de este diagnóstico se redactaron tres líneas de acción normativas y se tradujeron dos de ellas en párrafos articulados listos para incorporar al Manual de Evaluación y Calificación del Desempeño Académico de la Facultad (borrador de 62 artículos). En paralelo, se reparó editorialmente un manual de 30 páginas diseñado en SVG y se construyó, iterativamente, un sistema piloto funcional compuesto por tres maquetas HTML (Convenio de Desempeño Académico, Informe Anual de Actividades y Sistema de Evaluación por comisión), una integración con Google Sheets mediante Google Apps Script, y un panel HTML independiente de deliberación conjunta con cálculo automático de la calificación final ponderada (Art. 35). El desarrollo se fundamentó conceptualmente en el Modelo de Sistema Viable de Beer (Román Cortés, 2025) y se contrastó, en su dimensión de satisfacción del proceso, con evidencia reciente sobre evaluación del desempeño en organizaciones (Rodrigues et al., 2026). El resultado es un piloto operativo de extremo a extremo, aún no ejecutado con una comisión real, que traduce los tres hallazgos centrales del diagnóstico —separación explícita entre horas y nivel de desempeño, declaración voluntaria de circunstancias del período, y un sistema de deliberación trazable— en artefactos normativos y técnicos verificables.

**Palabras clave:** evaluación del desempeño académico; cibernética organizacional; Modelo de Sistema Viable; análisis temático; gobernanza universitaria; rúbrica holística.

---

## 1. Introducción

### 1.1 Contexto institucional

La FING-USACH regula la evaluación y calificación del desempeño de su cuerpo académico mediante la Resolución N.º 5949 de 2009 y sus modificaciones, complementada por el Decreto Universitario N.º 26 de 1986 (Reglamento de Carrera Académica). Sobre esa base normativa, la Facultad ha venido elaborando un nuevo *Manual de Evaluación y Calificación del Desempeño Académico* —un borrador de resolución de 62 artículos organizados en diez títulos (V2_ManualBorradorResolucion.docx)— que busca ordenar el proceso evaluativo mediante un Convenio de Desempeño Académico (CDA) anual, un Informe Anual de Actividades, y una Rúbrica General de Desempeño Académico de carácter holístico, en escala de 0 a 4 (Insuficiente, Condicional, Aceptable, Bueno, Sobresaliente), aplicada por comisiones de departamento y de facultad.

El propio borrador normativo declara, en sus considerandos, que el sistema debe "resguardar criterios de objetividad, imparcialidad, transparencia, trazabilidad y debido proceso" y considerar "la diversidad de trayectorias existentes en la Facultad de Ingeniería" (V2_ManualBorradorResolucion.docx, Considerandos 2 y 4). Sin embargo, antes de este proyecto no existía evidencia empírica sistemática sobre cómo la comunidad académica percibe el proceso vigente, ni un instrumento validado para levantarla.

### 1.2 Problema y preguntas que orientan el proyecto

El proyecto parte de tres constataciones que se irán demostrando a lo largo del informe: (a) el proceso de evaluación vigente no ha sido evaluado empíricamente antes de este diagnóstico; (b) el artículo 35 del borrador normativo determina la calificación final mediante una "suma ponderada" que usa las horas comprometidas como ponderador (Pi), lo que —sin una interpretación explícita— puede leerse como una medición de tiempo y no de calidad; y (c) las entrevistas exploratorias sugieren que trayectorias biográficas relevantes (maternidad, inicio de carrera, cambios de jornada) no tienen actualmente un cauce formal de reconocimiento en el proceso.

De estas constataciones se derivan las preguntas que guían el trabajo: ¿cuál es la percepción real de la comunidad académica sobre el proceso vigente y sobre los principios de un eventual rediseño? ¿Qué ajustes normativos concretos permiten explicitar que las horas ponderan pero no califican, sin alterar la fórmula institucional del artículo 35? ¿Cómo se puede declarar el contexto biográfico del académico sin convertirlo en un criterio discrecional u oculto? ¿Es posible construir y validar, en un piloto de bajo costo, un sistema funcional que ponga a prueba estas hipótesis de ajuste antes de proponerlas a los órganos colegiados de la Facultad?

### 1.3 Objetivos

**Objetivo general.** Diagnosticar la percepción institucional del proceso vigente de evaluación del desempeño académico en la FING-USACH y, a partir de ese diagnóstico, diseñar, redactar normativamente y prototipar un sistema piloto que ponga a prueba hipótesis concretas de ajuste.

**Objetivos específicos:**
1. Levantar y analizar temáticamente la percepción de actores clave (vicedecanaturas de Investigación y Desarrollo y de Docencia, académicos de jerarquía asistente) mediante entrevistas semiestructuradas.
2. Consultar cuantitativa y cualitativamente a una muestra no probabilística de académicos de la Facultad sobre el proceso vigente y sobre criterios transversales para su rediseño.
3. Sintetizar la evidencia documental disponible en un análisis institucional acotado a las fuentes del proyecto.
4. Formular líneas de acción normativas que ajusten las hipótesis del proyecto y traducir dos de ellas en artículos concretos, compatibles con la numeración vigente del borrador del Manual.
5. Reparar editorialmente el manual de referencia (formato SVG de 30 páginas) para su uso institucional.
6. Diseñar y construir un prototipo funcional de extremo a extremo —convenio, informe de actividades, evaluación por comisión, consolidación y deliberación— que permita ejecutar un piloto real de validación.

### 1.4 Alcance temporal y estructura del informe

El período cubierto va desde agosto de 2026, cuando se recolectó la evidencia empírica de base (entrevistas, consulta, propuesta de instrumento para comisiones evaluadoras), hasta el 7 de septiembre de 2026, fecha del último commit registrado en el repositorio del proyecto. El informe sigue una estructura IMRaD: la sección 2 expone el marco teórico; la sección 3, la metodología empleada en cada fase; la sección 4, los resultados obtenidos; la sección 5 discute los resultados a la luz del marco teórico y de sus limitaciones; la sección 6 concluye; y la sección 7 lista las referencias citadas. Un anexo final indexa los archivos del repositorio para trazabilidad.

---

## 2. Marco teórico y conceptual

### 2.1 Cibernética organizacional y el Modelo de Sistema Viable

El diseño conceptual del sistema de evaluación se fundamenta en el Modelo de Sistema Viable (*Viable System Model*, VSM) de Stafford Beer, aplicado específicamente a la evaluación del desempeño académico en educación superior por Román Cortés (2025) en *An Organisational Cybernetics-Based System for Comprehensive Academic Performance Evaluation in Higher Education*. Este trabajo —firmado por el mismo responsable institucional del presente proyecto, desde el Centro de Integración Ingeniería y Sociedad de la FING-USACH— modela la facultad y sus departamentos como sistemas viables recursivos, siguiendo la lógica de que "las universidades comprenden facultades, las facultades comprenden departamentos, y los departamentos comprenden individuos o grupos, cada nivel operando autónomamente dentro de su propio entorno pero conectado mediante gobernanza recursiva y bucles de retroalimentación" (Román Cortés, 2025, p. 3, traducción propia).

El modelo distingue cinco subsistemas (S1 a S5) que se replican en cada nivel de recursión (Beer, 1979, 1985; Espejo y Reyes, 2011, citados en Román Cortés, 2025):

- **Sistema 1 (operaciones):** en el nivel de facultad, los departamentos académicos; en el nivel de departamento, las actividades individuales y colectivas de cada académico en las cinco dimensiones institucionales (docencia, investigación, extensión y vinculación con el medio, asistencia técnica y administración académica).
- **Sistema 2 (coordinación):** los protocolos estandarizados, calendarios institucionales, rúbricas comunes y la plataforma digital de evaluación, que amortiguan oscilaciones e inconsistencias entre unidades.
- **Sistema 3 (control):** la asignación de recursos y la supervisión operativa que garantiza la homeostasis organizacional.
- **Sistema 3\* (auditoría independiente):** un mecanismo esporádico de verificación cruzada que confirma que la información que llega al Sistema 3 refleja fielmente lo ocurrido en el Sistema 1, evitando lo que Beer (1985) describe con la advertencia irónica "aquí no hay sorpresas" cuando ese canal está ausente.
- **Sistema 4 (inteligencia):** el escaneo del entorno y la planificación estratégica.
- **Sistema 5 (política e identidad):** la definición del propósito y la cohesión institucional.

Román Cortés (2025) aplica además la Ley de Variedad Requisita de Ashby (1956): solo la variedad puede absorber variedad, de modo que la diversidad de roles y evidencias académicas (docencia, investigación, gestión, vinculación) exige mecanismos reguladores diferenciados —*reductores* (normas, rúbricas, escalas unificadas) y *amplificadores* (tecnología de la información, convenios flexibles, portafolios digitales)— en equilibrio continuo. El aprendizaje organizacional se articula mediante el ciclo OADI (*Observe–Assess–Design–Implement*; Kim, 1993, citado en Román Cortés, 2025), distinguiendo aprendizaje de bucle simple (ajuste incremental) y de bucle doble (revisión de metas y normas) (Argyris, 1977, citado en Román Cortés, 2025). Este marco es el que sustenta, en el presente proyecto, la decisión de tratar el piloto no como una prueba de un formulario, sino como un mecanismo de aprendizaje institucional capaz de retroalimentar el propio Manual.

### 2.2 Satisfacción con la evaluación del desempeño: la retroalimentación como predictor

Para interpretar los hallazgos de la consulta a académicos (sección 4.2), se recurre a Rodrigues et al. (2026), quienes desarrollaron y validaron el *Satisfaction Questionnaire for Performance Appraisal Evaluation* (SQPAE) mediante cuatro estudios sucesivos (desarrollo de ítems, análisis factorial exploratorio, análisis factorial confirmatorio y un estudio de factores predictivos). El instrumento identifica tres dimensiones de la satisfacción con la evaluación del desempeño: procedimientos, efectividad y retroalimentación del proceso. Su cuarto estudio, con 450 profesionales, encontró que la retroalimentación (β = .427, p < .001) y la efectividad percibida (β = .253, p < .001) predicen significativamente la satisfacción con los resultados de la evaluación, mientras que los procedimientos no tuvieron efecto significativo directo; además, un modelo de mediación mostró que la retroalimentación media parcialmente la relación entre efectividad percibida y satisfacción (de β = .842 a β = .270, p < .001; prueba de Sobel Z = 8.214, p < .001) (Rodrigues et al., 2026, p. 7). Los autores concluyen que "la satisfacción de los empleados con la EP es esencial para maximizar el talento organizacional" y que "desarrollar herramientas válidas y precisas para evaluar la satisfacción con la EP es, por tanto, crítico" (Rodrigues et al., 2026, p. 8, traducción propia). Esta evidencia internacional es coherente —como se discute en la sección 5.1— con el hallazgo local de que la dimensión "utilidad formativa y retroalimentación" recibe apenas 43,6 % de acuerdo en la consulta a académicos de la FING-USACH.

### 2.3 Análisis temático de Braun y Clarke

El análisis de las cuatro entrevistas institucionales siguió el método de seis fases de Braun y Clarke (2006): (1) familiarización con los datos, (2) generación de códigos iniciales, (3) búsqueda de temas, (4) revisión de temas, (5) definición y denominación de temas, y (6) producción del informe. El enfoque adoptado fue inductivo y semántico, "buscando reflejar la realidad explícita manifestada por los académicos sobre su desempeño y evaluación" (Reporte Análisis Temático Entrevistas, 2026, Fase 3), sin imponer categorías teóricas previas a la codificación.

### 2.4 Fuentes de evidencia para una evaluación académica multidimensional

La literatura consultada para el diseño del Informe Anual de Actividades (documento interno *fuentes evidencias.docx*) coincide con la literatura internacional revisada por Román Cortés (2025) en que ningún indicador aislado es suficiente. En docencia, se recomienda triangular evidencia de estudiantes, pares, resultados de aprendizaje y autoevaluación reflexiva (HERDSA, s.f., citado en *fuentes evidencias.docx*); en investigación, publicaciones, financiamiento, informes a terceros y transferencia; en vinculación con el medio, la Comisión Nacional de Acreditación de Chile distingue criterios de "política y gestión" y de "resultados e impacto", advirtiendo que las universidades chilenas "usan manuales, instrumentos e indicadores, aunque con predominio cuantitativo y desafíos para medir impacto, contribución y bidireccionalidad de manera más cualitativa" (CNA Chile, s.f., citado en *fuentes evidencias.docx*). Esta literatura es consistente con la crítica identificada en las entrevistas (sección 4.1) al "conteo de horas" como métrica única de desempeño, y con hallazgos internacionales sobre las limitaciones de indicadores bibliométricos como el índice h para reflejar diferencias disciplinarias (Aksnes, Langfeldt y Wouters, 2019; Ding, Liu y Kandonga, 2020, citados en Román Cortés, 2025).

---

## 3. Metodología

El proyecto siguió un diseño mixto, secuencial y participativo, articulado en ocho fases: dos de diagnóstico (cualitativa y cuantitativa), una de síntesis restringida a fuentes documentales, dos normativas (líneas de acción y redacción articulada), una de reparación editorial de un artefacto normativo preexistente, y dos de desarrollo y validación de software.

### 3.1 Fase diagnóstica cualitativa: entrevistas y análisis temático

**Instrumentos.** Se aplicaron tres protocolos de entrevista semiestructurada diferenciados por rol (`PROTOCOLO DE ENTREVISTA ACADEMICO.docx`, `PROTOCOLO DE ENTREVISTA COMISION.docx`, `PROTOCOLO DE ENTREVISTA director.docx`), previo consentimiento informado (`Consentimiento_Informado_Entrevistas_FING_USACH.docx`).

**Muestra.** Cuatro entrevistas a informantes con roles directivos y docentes en la Facultad: Vicedecanato/a de Investigación y Desarrollo, Vicedecanato/a de Docencia, y dos académicos de jerarquía asistente con funciones de gestión.

**Análisis.** Se aplicó el método de seis fases de Braun y Clarke (2006), documentado en seis reportes sucesivos dentro de `Reporte Analisis Tematico Entrevistas.pdf`: familiarización (síntesis del corpus y memos analíticos por entrevista), codificación inicial (tabla de códigos con descripción y extracto representativo por entrevista), búsqueda de temas potenciales, revisión de temas (verificando homogeneidad interna y heterogeneidad externa en dos niveles: extractos/temas y mapa temático/corpus completo), definición y denominación final de los temas, y producción del informe con análisis integrado de convergencias y contrastes.

### 3.2 Fase diagnóstica cuantitativa: consulta a académicos

**Instrumento.** Consulta diagnóstica de siete ámbitos: caracterización de participantes, carga académica declarada, percepción del proceso vigente (seis dimensiones, escala 1–4), criterios transversales para un eventual rediseño (escala 1–4), evaluación del catálogo de actividades por área, fuentes de evidencia preferidas por área, instrumentos o mecanismos preferidos, prioridades de cambio, y dos preguntas abiertas.

**Muestra.** 55 respuestas válidas, no probabilísticas ni censales, de académicos de las diez unidades académicas de la Facultad; Eléctrica (23,6 %) e Industrial (18,2 %) concentran el 41,8 % de las respuestas. El 45,5 % tiene jerarquía de Asociado/a, 29,1 % Asistente y 23,6 % Titular. El 61,8 % declara haber sido evaluado/a con el proceso vigente; 38,2 % no lo ha sido o no está seguro/a.

**Análisis cuantitativo.** Estadística descriptiva (frecuencias, porcentajes, medias, umbral de "acuerdo" definido como las categorías 3–4 de la escala). La carga académica declarada, tratada como dato composicional (porcentajes que suman 100 % por persona), se analizó mediante un procedimiento exploratorio de clúster: transformación *centered log-ratio* (CLR) de las siete áreas declaradas, seguida de *k-means* con evaluación de soluciones mediante el coeficiente de silueta promedio; la solución de seis clústeres (*k* = 6) obtuvo el mejor ajuste (silueta = 0,383) y fue adoptada como solución final.

**Análisis cualitativo.** 150 comentarios abiertos, aportados por 50 personas, se codificaron temáticamente con apoyo de un diccionario de codificación asistida, generando 476 asignaciones temáticas sobre 12 temas (T01–T12) y 13 comentarios sin codificación automática.

### 3.3 Fase de síntesis: análisis institucional restringido a fuentes documentales

Por instrucción metodológica explícita, se elaboró un análisis institucional de exactamente 250 palabras bajo una restricción estricta: sin recurrir a fuentes externas a la conversación de trabajo ni a memoria ajena a los documentos cargados en el repositorio (sección 3.1 y 3.2 más los documentos normativos y de literatura). Este control metodológico buscó asegurar que la síntesis institucional se fundamentara exclusivamente en la evidencia empírica y documental verificable del proyecto, sin proyecciones no sustentadas.

### 3.4 Fase normativa: líneas de acción y redacción articulada

A partir del análisis institucional, se redactaron tres líneas de acción (150 palabras exactas cada una) dirigidas a ajustar las hipótesis del proyecto en tres alcances: la función de las horas en el artículo 35, el reconocimiento de trayectorias y circunstancias biográficas, y el rediseño del piloto. Dos de estas líneas se tradujeron después en párrafos normativos concretos, redactados para incorporarse como texto nuevo dentro de artículos ya existentes del borrador del Manual, sin alterar su numeración, sus referencias cruzadas ni la fórmula institucional del artículo 35.

### 3.5 Fase de reparación editorial del manual (SVG)

El manual de referencia (`Manual_Evaluacion_prototipo_30_limpio.svg`, 30 páginas A4, 10 títulos normativos) presentaba errores estructurales heredados de su diseño en Inkscape. La reparación se ejecutó mediante una infraestructura de automatización construida ad hoc: scripts de PowerShell (`New-FromTemplate.ps1`, `Export-Diagram.ps1`, `Invoke-InkscapeAction.ps1`) que invocan la CLI de Inkscape 1.x para manipular el SVG por selección de identificadores de objeto, integrados como tareas de Visual Studio Code. Sobre esa infraestructura se ejecutaron cinco fases secuenciales de corrección (detalladas en la sección 4.5), cada una validada visualmente página por página antes de avanzar a la siguiente.

### 3.6 Fase de desarrollo de software: maquetas, integración y panel de deliberación

Se adoptó un enfoque de prototipado rápido con HTML5, CSS y JavaScript vainilla, sin dependencias de *build* ni frameworks, priorizando la portabilidad (archivos autocontenidos, ejecutables abriendo el archivo directamente en el navegador) sobre la complejidad arquitectónica, consistente con el criterio explícito del proyecto de tratar cada artefacto como maqueta funcional y no como producto terminado. Para la persistencia de datos del piloto (tres comisionados evaluando un caso) se evaluaron alternativas (servidor con base de datos, Google Forms, Google Sheets) y se optó por Google Sheets con un backend sin servidor en Google Apps Script, por su bajo costo de implementación y su familiaridad para la Secretaría Técnica. La deliberación conjunta de la comisión se desacopló posteriormente de Google Sheets y se implementó como una interfaz HTML independiente que consume un archivo JSON exportado, decisión justificada por la necesidad de que la comisión delibere en un sistema propio y no directamente sobre la planilla de datos brutos.

### 3.7 Validación y control de calidad iterativo

Cada corrección de código se validó antes de confirmarse (*commit*) mediante extracción y ejecución del script JavaScript con Node.js fuera del navegador, simulando la lógica de cálculo (por ejemplo, la exclusión de áreas no ejecutadas del cálculo ponderado, o la coincidencia de horas totales entre el sistema de evaluación y el panel de deliberación) antes de su verificación visual en el navegador. Este control de calidad permitió detectar y documentar errores reales de especificidad CSS y de lógica de cálculo, descritos en la sección 4.7.

---

## 4. Resultados

### 4.1 Resultados del diagnóstico cualitativo

El análisis temático identificó cuatro temas finales, cada uno con dos subtemas, sustentados en extractos representativos de las cuatro entrevistas:

**Tema 1. Identidad académica en tensión: el ideal de integridad frente a la fragmentación del rol.** Los participantes definen su labor como un "reservorio de conocimiento" orientado a la búsqueda de la verdad y su transferencia social ("Investigación tiene una sola definición y es la búsqueda de la verdad"), identidad que colisiona con una estructura administrativa que "tapa" el tiempo sustantivo ("la gestión administrativa no te permite mucho avanzar en el resto... ahí hay una sobrecarga importante").

**Tema 2. Condiciones institucionales limitantes: deficiencias de infraestructura y soporte.** Los cuatro entrevistados señalan de manera unánime que la excelencia exigida no está respaldada por condiciones materiales mínimas: climatización de salas, software especializado y personal técnico de apoyo ("la universidad no puede exigirte hacer investigación si la universidad no te asegura los recursos"; "la sala donde hago clases no tiene aire acondicionado... la infraestructura te empuja a hacer clases más bien tradicionales").

**Tema 3. Insuficiencia del modelo de evaluación actual: el desfase entre cantidad y calidad.** Se critica el paradigma de "conteo de horas cronológicas" y la ausencia casi total de retroalimentación formativa post-evaluación ("el problema que tiene el manual ese famoso es que lo que evalúa es si es que la persona usó las 8 horas... se confunden el tiempo con la calidad"; "no siento que me evalúen a nivel académico... no hay ningún tipo de medición en la parte docente y tampoco retroalimentación"; "no me ayuda a mejorar... estoy ciego... no tengo esa retroalimentación").

**Tema 4. Hacia una evaluación justa: diferenciación por perfiles y alineación estratégica.** Se demanda reconocer trayectorias diversas y contextos vitales, explícitamente el impacto de la maternidad en la productividad ("el tema de la maternidad, porque eso no se considera en ninguna parte... estoy compitiendo con hombres que tuvieron 5 años para producir mientras tú tuviste tres"; "tienes que ver qué es lo que pasó con la historia y la trayectoria... un cabro que recién sacó el doctorado... no le puedes decir 'usted ganó cero proyectos'").

La convergencia principal entre los cuatro entrevistados es el rechazo al registro de horas cronológicas como proxy de calidad, y el consenso en que la falta de retroalimentación es la falla sistémica más crítica. El informe cierra con una síntesis metafórica: la Facultad funciona "como una orquesta de excelencia que debe tocar en un escenario sin acústica y con instrumentos desafinados: el talento y la voluntad existen, pero el entorno material y el sistema de evaluación... no permiten que la obra alcance su máximo esplendor" (Reporte Análisis Temático Entrevistas, 2026, Fase 6).

### 4.2 Resultados del diagnóstico cuantitativo

**Percepción del proceso vigente.** Ninguna de las seis dimensiones evaluadas alcanza una media de 3,0 en la escala 1–4: claridad y transparencia (M = 2,8; 61,8 % de acuerdo), objetividad/consistencia/confianza (M = 2,6; 55,2 %), carga administrativa y factibilidad operativa (M = 2,5; 52,1 %), pertinencia respecto del trabajo académico realizado (M = 2,4; 42,4 %), utilidad formativa y retroalimentación (M = 2,3; 43,6 %), y reconocimiento de perfiles, trayectorias y contextos (M = 2,15; 33,9 % de acuerdo) —la dimensión peor evaluada de las seis—.

**Nudos críticos.** Los ocho ítems con mayor desacuerdo convergen en un mismo problema —el proceso diferencia débilmente entre perfiles, trayectorias, condiciones de trabajo y calidad del desempeño—: condiciones institucionales disponibles (70,9 % desacuerdo), reconocimiento de diferencias entre perfiles académicos y tipos de contribución (63,6 %), valoración de calidad e impacto más allá del cumplimiento formal de horas/actividades (63,6 %), consideración de jerarquía y etapa de trayectoria académica (63,6 %), retroalimentación suficiente sobre fortalezas y aspectos a mejorar (60,0 %), reflejo adecuado de la complejidad del trabajo académico realizado (58,2 %), información útil para mejorar el desempeño académico (56,4 %) y proporcionalidad entre el tiempo de preparación y la utilidad real del proceso (56,4 %).

**Criterios transversales para el rediseño.** En contraste directo con la evaluación negativa del proceso vigente, los tres criterios propuestos para un eventual rediseño reciben niveles altos de acuerdo: coherencia entre actividades, responsabilidad, jerarquía y perfil (M = 3,5; 92,7 % de acuerdo), cumplimiento de compromisos acordados (M = 3,3; 90,9 %) y calidad, contribución o impacto (M = 3,3; 83,6 %). Mientras 0 de 6 dimensiones del proceso vigente alcanza media 3,0, las 3 de 3 dimensiones del rediseño propuesto superan 83,6 % de acuerdo.

**Análisis de clúster de la carga académica declarada.** Sobre 55 observaciones, la solución de seis clústeres (silueta promedio = 0,383) distingue perfiles de composición de actividades: C1 "Gestión académica intensiva" (n = 4; 7,3 %; Administración Académica 41,2 % de la carga media), C2 "Docencia–I+D con extensión" (n = 9; 16,4 %), C3 "Mixto con gestión" (n = 15; 27,3 %; el clúster más numeroso), C4 "Docencia diversificada" (n = 5; 9,1 %), C5 "Mixto con asistencia técnica" (n = 10; 18,2 %) y C6 "I+D–docencia con extensión" (n = 12; 21,8 %). En conjunto, docencia (38,7 %) e investigación y desarrollo (32,0 %) concentran el 70,7 % de la carga académica media declarada; docencia es la única área con 100 % de cobertura (todos los participantes declaran carga mayor que cero).

**Evaluación del catálogo de actividades por área.** Cruzando representatividad del trabajo real y claridad estructural, Perfeccionamiento resulta el área más consolidada (89,1 % de acuerdo en representatividad; 87,3 % en claridad estructural), seguida de Docencia (89,1 %; 63,6 %, con una brecha de 25,5 puntos porcentuales entre ambos criterios). Asistencia Técnica es el caso más crítico: 65,5 % de acuerdo en representatividad, 58,2 % en claridad estructural, y el mayor porcentaje de respuestas "sin antecedentes suficientes" (28,2 %).

**Fuentes de evidencia e instrumentos preferidos.** No existe una fuente única de evidencia preferida entre todas las áreas: la fuente más seleccionada en cada área concentra entre 50,9 % y 78,2 % de las menciones, y varía según el área (jefaturas/coordinación docente en Docencia, bases de indexación en I+D, autoridades o jefaturas en Administración Académica). El instrumento más preferido para el rediseño es una "pauta específica por área académica" (50,9 %), seguida de rúbricas generales (45,5 %), retroalimentación formal con plan de mejora (45,5 %) y portafolio o expediente académico digital (40,0 %).

**Prioridades de cambio.** "Reconocer perfiles académicos diferenciados" es la prioridad principal declarada (78,2 %), seguida de "reducir el énfasis en horas cronológicas" (52,7 %); un bloque de cambios operativos y sustantivos ronda el 40 % (simplificar la carga administrativa, incorporar un portafolio académico estructurado, reconocer gestión académica no formalizada, incorporar criterios de calidad e impacto).

**Análisis cualitativo de respuestas abiertas.** Sobre 150 comentarios de 50 personas (476 asignaciones temáticas), el tema más extendido es "Comisión/gobernanza" (T09; mencionado por 35 personas, 63,6 %), seguido de "Perfiles/trayectoria" (T05; 31 personas, 56,4 %) y "Claridad normativa" (T01; 28 personas, 50,9 %). El tema de gobernanza no aparece aislado: sus mayores coocurrencias son con objetividad/confianza (32 menciones conjuntas), claridad normativa (31) y carga administrativa (27), lo que sugiere que la legitimidad del proceso se juega en la composición de comisiones, las reglas explícitas y la trazabilidad de decisiones, no solo en la existencia de criterios. Al comparar la presencia temática entre "problemas del proceso actual" y "mejoras propuestas", los problemas se concentran en gobernanza (24 menciones) y claridad normativa (21), mientras las mejoras propuestas se desplazan hacia perfiles (23), catálogo (13) y retroalimentación (14) —un desplazamiento del diagnóstico negativo hacia una agenda operativa de rediseño—.

### 4.3 Síntesis integradora: análisis institucional restringido a fuentes

El análisis de 250 palabras producido en esta fase (`analisis_evaluacion_desempeno_FING.md`) sintetiza la asimetría central del proyecto: el diagnóstico está mucho mejor validado que la propuesta normativa, que a la fecha del análisis permanecía sin validación experta ni piloto operativo. Identificó tres riesgos que orientaron directamente las líneas de acción normativas (sección 4.4): la exigencia de "condiciones institucionales" (70,9 % de rechazo) excede el alcance de un manual que regula juicio y procedimiento, no la asignación de recursos; el artículo 35 mantiene las horas como ponderador aun cuando el nivel se juzga cualitativamente, con riesgo de leerse como "simulación de cambio" si esa continuidad no se explicita; y maternidad y trayectorias biográficas, presentes explícitamente en las entrevistas, no estaban operacionalizadas en el borrador normativo pese a ser la dimensión peor evaluada cuantitativamente (M = 2,15).

### 4.4 Líneas de acción y propuestas normativas

Las tres líneas de acción (`lineas_accion_ajuste_hipotesis.md`) proponen, respectivamente: (1) explicitar en los artículos 35 y 36 que las horas comprometidas operan como ponderador de dedicación y no como medida de desempeño, ilustrando la separación con el caso importado del proyecto (2.070 horas realizadas frente a 1.944 horas comprometidas), mostrando nivel y ponderación en campos separados del sistema, nunca sumados; (2) convertir el contexto biográfico en un campo declarable, voluntario y confidencial dentro del CDA, cuyo único efecto sea ajustar el volumen de compromisos esperado sin alterar la exigencia de calidad ni la escala de evaluación; y (3) reconvertir el piloto para que ponga a prueba, además del sistema, estas dos hipótesis normativas, agregando mediciones de divergencia entre evaluadores, calidad de la fundamentación escrita y comprensión de la separación horas/nivel, y cerrando con el instrumento de 15 ítems Likert más 2 preguntas abiertas ya diseñado para comisiones evaluadoras (`Propuesta_Instrumento_Comisiones_Evaluadoras.pdf`) como post-test de los evaluadores.

Estas líneas se tradujeron en dos conjuntos de párrafos normativos concretos:

**Línea de acción 1 (`propuesta_art35_funcion_horas.md`).** Se propone un nuevo párrafo del artículo 35 que fija que el factor Pi "opera exclusivamente como ponderador de la importancia relativa" de cada actividad, y que el factor Ni "provendrá siempre del juicio académico fundado de la comisión... considerando la evidencia verificable presentada, el rol desempeñado, la coherencia con la jerarquía académica y la jornada contractual, y el alcance o contribución del desempeño demostrado", prohibiendo explícitamente sustituir ese juicio por el cómputo de horas. Un segundo párrafo, para el artículo 36, establece que la diferencia entre horas comprometidas y realizadas "no modificará por sí sola el nivel de desempeño asignado": ni un exceso de horas sube automáticamente el nivel, ni un déficit lo baja si la evidencia sostiene el cumplimiento; si la diferencia es relevante para compromisos críticos, la comisión debe dejar constancia fundada en el expediente. Cabe destacar —como se discute en la sección 5.2— que el borrador normativo ya contenía, en su artículo 36, una regla afín pero más acotada: que un área *no comprometida* en el CDA no debe calificarse con nivel cero por la sola ausencia de actividad, salvo que contradiga exigencias mínimas institucionales (V2_ManualBorradorResolucion.docx, Art. 36). La propuesta de la línea de acción 1 generaliza ese principio a la relación entre horas y nivel dentro de cualquier área, comprometida o no.

**Línea de acción 2 (`propuesta_trayectorias_maternidad.md`).** Se proponen tres párrafos nuevos: en el artículo 23, una sección voluntaria y confidencial (protegida por el artículo 52 de reserva) de "circunstancias del período" —descanso pre y postnatal, permiso postnatal parental, responsabilidades de cuidado, licencias médicas prolongadas, inicio de carrera tras el grado, cambios de jornada—, conocida solo por el Director/a de Departamento y la comisión evaluadora, cuyo único efecto es ajustar el volumen de compromisos al formalizar el convenio, sin incidir en la exigencia de calidad, la escala del artículo 37, la Rúbrica General ni los rangos del artículo 35; en el artículo 25, la posibilidad de solicitar modificación excepcional del CDA cuando estas circunstancias sobrevienen con posterioridad a su formalización; y en el artículo 34, la obligación de la comisión de dejar constancia del ajuste aplicado (sin detallar su naturaleza) al fundamentar su evaluación, bajo sanción de reclamo por omisión de fundamentación (Art. 54).

### 4.5 Reparación editorial del manual (SVG)

El manual `Manual_Evaluacion_prototipo_30_limpio.svg` (30 páginas A4, 10 títulos) se corrigió en cinco fases secuenciales, cada una verificada visualmente antes de avanzar: (A) `viewBox` multipágina roto, casos de color inconsistentes, texto vacío o corrupto y superposición de títulos; (B) normalización de la escala tipográfica, de 76 tamaños de fuente distintos a un sistema de aproximadamente 10, con mínimo legible de 8 puntos; (C) colisiones de contenido con el pie de página en ocho páginas (04, 06, 12, 14, 19, 24, 27, 28), resueltas mediante compresión vertical por tramos, con corrección posterior de regresiones residuales en líneas de pie y bordes de tarjetas; (D) reparación de un componente de flujo de pasos roto y limpieza de fragmentos de ícono o texto duplicados/huérfanos en las páginas 10, 11, 12, 15, 18 y 27; y (E) corrección de títulos y texto cortado o superpuesto en las páginas 27 y 28, con verificación final de las 30 páginas completas. Posteriormente se incorporó una versión de avance más extensa (`avance_manual.svg`) junto con su especificación editorial normalizada (`manual_desempeno_especificacion_editorial_CORREGIDA.md`), un documento técnico que fija la fuente única de reconstrucción programática del manual (formato A4 210×297 mm, tipografías Noto Sans/Noto Serif Display exclusivamente, texto editable sin conversión a curvas) con reglas explícitas de precedencia sobre orden de páginas, corrección de desbordes y prohibición de residuos duplicados.

### 4.6 Sistema piloto desarrollado

**Convenio de Desempeño Académico** (`convenio_desempeno_maqueta.html`), diseñado conforme a los principios documentados en `formato_convenio_desempeno.md`: una hoja de compromisos, la fila como unidad evaluable ("la comisión evalúa filas, no párrafos"), la ponderación como peso relativo y no como calificación, el contexto declarado en hoja aparte, y datos de identificación precargados y escritos una sola vez. Define cinco validaciones previas a la formalización (suma de ponderaciones = 100 %, evidencia declarada por fila, mínimos normativos cubiertos o justificados, roles asociados, y advertencia —no bloqueo— por exceso de compromisos).

**Informe Anual de Actividades** (`informe_actividades_maqueta.html`), maqueta de reporte de lo efectivamente realizado en el período.

**Sistema de Evaluación por comisión** (`sistema_evaluacion_maqueta_v2.html`), estructurado en tres pasos: identificación del comisionado y declaración de conflicto de interés (Arts. 50–51); antecedentes y evaluación de siete áreas mediante un modal que incorpora la Rúbrica General (escala 0–4), fundamentación obligatoria —reforzada para los niveles 0, 1 y 4, conforme al numeral 5.6 del Anexo I— y una Guía Orientadora filtrada por jerarquía cuando existe (actualmente solo para Docencia e Investigación y Desarrollo); y registro de tiempo empleado, incidentes y envío. La vista preliminar de calificación final se etiqueta explícitamente como "preliminar y personal — no constituye la calificación final: esa surge de la deliberación conjunta de la comisión".

**Integración con Google Sheets** (`apps_script_deliberacion.gs`, `sistema_deliberacion_estructura.md`, `IMPLEMENTACION_GOOGLE_SHEETS.md`): cada comisionado envía su evaluación por POST a un Google Apps Script que valida el payload, escribe una fila en la hoja "Datos brutos" y recalcula automáticamente la hoja "Consolidación" —las tres evaluaciones lado a lado por área, con cálculo de divergencia (máximo menos mínimo) y semáforo de consenso—.

**Panel de deliberación independiente** (`panel_deliberacion.html`), que recibe un JSON exportado desde la planilla consolidada y no depende del backend de Sheets. Incluye un cuadro resumen por área (las 7 áreas × 3 comisionados, con estado de divergencia y nivel acordado actualizado en vivo), evaluaciones lado a lado con fundamento citado por comisionado, un selector de nivel acordado (0–4) con notas de deliberación por área, cálculo dinámico de la calificación final ponderada por las horas reales del académico, un panel de firmas conforme al artículo 52 y Título IX, y generación de un acta descargable en formato JSON con timestamp, deliberaciones, calificación final y firmas.

### 4.7 Iteraciones de corrección y reglas de negocio

El desarrollo del panel de deliberación evidenció, mediante el control de calidad descrito en la sección 3.7, tres correcciones sustantivas:

1. **Incompatibilidad de estructura de datos** entre el JSON exportado y el código del panel, resuelta con acceso tolerante a ambas variantes de estructura (*optional chaining*).
2. **Error de especificidad CSS en el botón de nivel seleccionado**: la regla `[data-n="3"]` (color de texto azul, propio del nivel) tenía la misma especificidad que la clase `.sel` (color de texto blanco) pero se declaraba después en la hoja de estilos, por lo que ganaba sobre el color blanco esperado, dejando el botón seleccionado casi ilegible sobre fondo índigo. Se corrigió usando el color semántico de cada nivel como fondo sólido al seleccionar, preservando la codificación de color (rojo/naranja/gris/azul/verde) con texto blanco legible.
3. **Error de cálculo real**: la función que calcula la calificación final usaba un arreglo de horas fijo en el código (*hardcodeado*) en lugar de leer las horas reales (`areas_horas`) del JSON cargado, por lo que la calificación final nunca reflejaba la jornada efectivamente comprometida por el académico evaluado. Corregido para leer los datos reales, verificado mediante simulación en Node.js.
4. **Regla de negocio explícita:** si un académico comprometió una actividad en el CDA pero no la ejecutó durante el período (0 horas realizadas), esa área no se muestra para evaluación —no exige nivel 0–4 ni bloquea el envío— y se excluye del cálculo ponderado de la calificación final, con una nota de transparencia visible para la comisión. Esta regla se implementó primero en el sistema de evaluación y luego, por consistencia, en el panel de deliberación, que ahora calcula dinámicamente el conjunto de áreas aplicables como la intersección de las áreas efectivamente evaluadas por los tres comisionados, en lugar de asumir una lista fija de siete áreas. Como se señala en la sección 4.4, esta regla generaliza, para el caso de actividades comprometidas pero no ejecutadas, el principio ya presente en el artículo 36 del borrador normativo para actividades no comprometidas.

Cada corrección fue validada extrayendo y ejecutando la lógica de JavaScript en Node.js antes de confirmarse en el repositorio, verificando tanto la sintaxis como el resultado numérico del cálculo (por ejemplo, comprobando que el total de horas ponderadas coincidiera entre el sistema de evaluación y el panel de deliberación tras excluir un área sin ejecutar: 41 horas en ambos, frente a las 44 horas totales originales).

---

## 5. Discusión

### 5.1 Convergencia cuali-cuantitativa: gobernanza como nudo articulador

Los resultados cualitativos y cuantitativos convergen con notable consistencia interna. El tema cualitativo más extendido —"Comisión/gobernanza" (63,6 % de menciones)— coincide con el hallazgo cuantitativo de que "objetividad, consistencia y confianza" es la segunda dimensión peor evaluada (M = 2,6) y con que "reconocer diferencias entre perfiles académicos y tipos de contribución" concentra 63,6 % de desacuerdo. Esta triangulación es relevante porque el problema no se localiza únicamente en la comprensión de la normativa vigente —de hecho, "claridad y transparencia" es la dimensión relativamente mejor evaluada, aunque tampoco supera 3,0 (M = 2,8)— sino en la capacidad institucional de las comisiones para representar la diversidad del trabajo académico de forma consistente y confiable. Leído desde el marco de Román Cortés (2025), este hallazgo señala directamente una debilidad en los Sistemas 2 y 3\* del modelo aplicado a la FING-USACH: la ausencia de un mecanismo de coordinación estandarizada (System 2) que amortigüe divergencias interpretativas entre comisiones de distintos departamentos, y la ausencia —diagnosticada explícitamente en el propio marco teórico como "no sistemáticamente implementada" (Román Cortés, 2025, p. 18, traducción propia)— de un canal de auditoría independiente (System 3\*) que verifique la coherencia de los reportes departamentales antes de que lleguen al nivel de facultad. El panel de deliberación desarrollado en este proyecto (sección 4.6) constituye, en esos términos, un intento concreto de operacionalizar tanto un reductor de variedad (una rúbrica y un procedimiento de deliberación comunes a toda evaluación) como un transductor (la consolidación automática de tres juicios individuales en un registro trazable y firmado), en la línea de lo que el marco teórico denomina "matrices de consistencia digital" y "registros electrónicos estandarizados" (Román Cortés, 2025, p. 19).

### 5.2 El nudo horas/calidad a la luz de la literatura de evaluación académica

La crítica unánime de las cuatro entrevistas al "conteo de horas" como proxy de calidad, y el 63,6 % de desacuerdo cuantitativo con que hoy "se valora calidad e impacto más allá del cumplimiento formal de horas/actividades", son coherentes con una literatura internacional amplia sobre las limitaciones de las métricas cuantitativas únicas en evaluación académica: los índices bibliométricos "han demostrado reflejar inadecuadamente las diferencias disciplinarias" y ser vulnerables a la manipulación (Aksnes et al., 2019; Ding et al., 2020, citados en Román Cortés, 2025, p. 2); documentos de buenas prácticas como el Manifiesto de Leiden urgen a que los indicadores "se interpreten en contexto, se trianguen con juicio cualitativo y se adapten a la diversidad disciplinaria" (Hicks et al., 2015, citado en Román Cortés, 2025, p. 3). La propuesta normativa de la línea de acción 1 (sección 4.4) responde directamente a esta tensión, no eliminando el ponderador de horas —que la Resolución 5949/2009 y la fórmula vigente del artículo 35 mantienen— sino resignificándolo explícitamente como medida de dedicación relativa y no de desempeño, evitando lo que el análisis institucional de síntesis anticipó como riesgo de que la continuidad formal con la resolución vigente "se lea como simulación de cambio, no como anclaje normativo deliberado" (`analisis_evaluacion_desempeno_FING.md`). La regla de negocio implementada en el sistema piloto (sección 4.7, punto 4) —excluir del cálculo ponderado las áreas comprometidas pero no ejecutadas— es la traducción técnica directa de esta hipótesis normativa: en la práctica, hace imposible que la ausencia de horas realizadas, por sí sola, arrastre a la baja la calificación ponderada, sin necesidad de que la comisión fuerce un nivel 0 no fundamentado en evidencia.

### 5.3 Trayectorias, maternidad y equidad: la dimensión peor evaluada

"Reconocimiento de perfiles, trayectorias y contextos" es la dimensión peor evaluada del proceso vigente (M = 2,15; 33,9 % de acuerdo) y, simultáneamente, la prioridad principal declarada para el rediseño (78,2 %). Las entrevistas dan densidad cualitativa a esta cifra: el testimonio sobre "competir con hombres que tuvieron 5 años para producir mientras tú tuviste tres" evidencia que la ausencia de reconocimiento formal de la maternidad no es un vacío procedimental neutro, sino una fuente de desventaja comparativa sistemática dentro del propio proceso de calificación. La propuesta de la línea de acción 2 (sección 4.4) resuelve esta tensión con un diseño deliberadamente acotado: la declaración de circunstancias del período ajusta *volumen* de compromisos, nunca *calidad* exigida ni escala de evaluación, y opera bajo reserva del artículo 52, conocida solo por quienes formalizan y evalúan el convenio. Este diseño responde a la doble exigencia identificada en el diagnóstico: que el contexto se reconozca (evitando la "invisibilidad del factor maternidad" nombrada en las entrevistas) sin que se convierta en "un criterio oculto" que reduzca la transparencia del proceso (riesgo señalado explícitamente en el propio análisis institucional). La obligación de dejar constancia del ajuste —sin revelar su naturaleza— en el artículo 34 es el mecanismo concreto que intenta sostener simultáneamente confidencialidad y trazabilidad.

### 5.4 El piloto como mecanismo de aprendizaje organizacional

Interpretado bajo el ciclo OADI (Observe–Assess–Design–Implement; Kim, 1993, citado en Román Cortés, 2025), el proyecto completo puede describirse como un primer giro de ese ciclo a nivel de facultad: la fase de observación (entrevistas y consulta, sección 4.1–4.2) generó evaluación (síntesis institucional, sección 4.3), que a su vez generó diseño (líneas de acción y redacción normativa, sección 4.4) y comienza a implementarse (sistema piloto, sección 4.6). Sin embargo, el propio marco teórico advierte que la viabilidad del sistema depende de que ese ciclo se cierre con retroalimentación real desde la operación hacia la norma —aprendizaje de bucle doble, no solo de bucle simple (Argyris, 1977, citado en Román Cortés, 2025)—. En ese sentido, el diseño del piloto (línea de acción 3, sección 4.4), que agrega mediciones explícitas de divergencia entre evaluadores, calidad de fundamentación y comprensión de las reglas nuevas, y que cierra con el instrumento de percepción de comisiones evaluadoras (`Propuesta_Instrumento_Comisiones_Evaluadoras.pdf`) como post-test, es la pieza metodológica que permitiría, en su ejecución real, cerrar ese bucle: convertir la experiencia operativa de tres comisionados evaluando un caso en evidencia capaz de confirmar, refutar o ajustar las hipótesis normativas antes de proponerlas formalmente a los órganos colegiados de la Facultad.

### 5.5 Limitaciones

El diagnóstico cuantitativo se basa en una muestra por conveniencia, no probabilística ni censal (55 de aproximadamente 180 académicos), con sobrerrepresentación de las unidades de Eléctrica e Industrial (41,8 % conjunto), por lo que sus medias y porcentajes deben leerse como descriptivos del grupo que respondió y no como estimaciones representativas de toda la planta académica —advertencia que el propio reporte de consulta formula explícitamente—. El diagnóstico cualitativo se apoya en solo cuatro entrevistas, todas de informantes con funciones directivas o de gestión, sin representación directa de académicos sin responsabilidades administrativas ni de jerarquías Titulares plenas. Las propuestas normativas y el sistema piloto no han sido validados aún por un comité experto ni ejecutados con una comisión real evaluando un caso real, tal como advertía explícitamente el análisis institucional de síntesis desde el inicio del proyecto: "la validación experta y el piloto operativo... siguen pendientes" (`analisis_evaluacion_desempeno_FING.md`). El instrumento de comisiones evaluadoras (`Propuesta_Instrumento_Comisiones_Evaluadoras.pdf`) fue diseñado pero no aplicado a la fecha de este informe. Finalmente, la interpretación de los hallazgos de satisfacción mediante el marco de Rodrigues et al. (2026) es análoga y no directa: el SQPAE fue validado en organizaciones del sector privado portugués, no en instituciones de educación superior chilenas, por lo que su aplicación aquí es orientadora y no una transferencia empírica directa.

---

## 6. Conclusiones

1. El diagnóstico mixto (cuatro entrevistas analizadas temáticamente y una consulta a 55 académicos) muestra un patrón consistente: la comunidad académica de la FING-USACH rechaza el proceso de evaluación vigente en sus seis dimensiones evaluadas (ninguna alcanza media 3,0 sobre 4,0) pero preaprueba, con alto acuerdo (83,6 %–92,7 %), los principios propuestos para su rediseño —coherencia entre actividades y perfil, cumplimiento de compromisos, y calidad o impacto—. El problema diagnosticado no es la existencia de normativa, sino su operacionalización: gobernanza, diferenciación de perfiles y retroalimentación formativa.

2. Las dos hipótesis normativas priorizadas por el diagnóstico —la función ponderadora, no calificadora, de las horas comprometidas (Art. 35–36), y la declaración voluntaria y confidencial de circunstancias del período para ajustar volumen sin afectar calidad (Art. 23, 25, 34)— fueron traducidas en párrafos normativos concretos, compatibles con la numeración y la fórmula institucional vigentes, listos para someterse a discusión y validación experta.

3. El sistema piloto desarrollado —convenio, informe de actividades, evaluación individual por comisión, consolidación automática en Google Sheets y deliberación conjunta en un panel HTML independiente— constituye una implementación funcional de extremo a extremo de ambas hipótesis normativas: separa explícitamente nivel y ponderación en la interfaz de evaluación, y excluye del cálculo ponderado las áreas comprometidas pero no ejecutadas, evitando que la ausencia de horas, por sí sola, penalice la calificación final.

4. El desarrollo del sistema evidenció la utilidad de un control de calidad iterativo basado en simulación de la lógica de negocio fuera del navegador (Node.js) antes de cada confirmación de cambios, que permitió detectar y corregir errores reales de cálculo (horas fijas en lugar de reales) y de interfaz (especificidad CSS) que habrían comprometido la validez de los resultados del piloto si hubiesen llegado sin corregir a una ejecución real.

5. El proyecto queda, al 7 de septiembre de 2026, en condiciones de iniciar su fase pendiente más crítica: la ejecución del piloto operativo real con una comisión de tres personas evaluando un caso, la aplicación del instrumento de percepción de comisiones evaluadoras como post-test, y la medición de divergencia entre evaluadores y comprensión de las reglas normativas nuevas —el conjunto de evidencia que, en palabras del propio análisis institucional que originó el proyecto, convertiría "legitimidad percibida en legitimidad operativa" (`analisis_evaluacion_desempeno_FING.md`).

---

## 7. Referencias

Argyris, C. (1977). Double loop learning in organizations. *Harvard Business Review*.

Ashby, W. R. (1956). *An introduction to cybernetics*. Chapman & Hall.

Aksnes, D. W., Langfeldt, L., & Wouters, P. (2019). Citations, citation indicators, and research quality: An overview of basic concepts and theories. *Sage Open*, *9*(1), 2158244019829575. https://doi.org/10.1177/2158244019829575

Beer, S. (1979). *The heart of enterprise: A model for the management of complexity*. Wiley.

Beer, S. (1985). *Diagnosing the system for organisations*. Wiley.

Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. *Qualitative Research in Psychology*, *3*(2), 77–101. https://doi.org/10.1191/1478088706qp063oa

Ding, J., Liu, C., & Kandonga, G. A. (2020). Exploring the limitations of the h-index and h-type indexes in measuring the research performance of authors. *Scientometrics*, *122*, 1303–1322. https://doi.org/10.1007/s11192-020-03364-1

Espejo, R., & Harnden, R. (Eds.). (1989). *The viable system model: Interpretations and applications of Stafford Beer's VSM*. Wiley.

Espejo, R., & Reyes, A. (2011). *Organizational systems: Managing complexity with the viable system model*. Springer.

Hicks, D., Wouters, P., Waltman, L., de Rijcke, S., & Rafols, I. (2015). The Leiden Manifesto for research metrics. *Nature*, *520*(7548), 429–431. https://doi.org/10.1038/520429a

Kim, D. H. (1993). The link between individual and organizational learning. *Sloan Management Review*, *35*(1), 37–50.

Rodrigues, R. I., Silva, A. J., & Lopes, C. (2026). Development and validation of a Satisfaction Questionnaire for Performance Appraisal Evaluation (SQPAE): a measurement instrument. *Psicologia: Reflexão e Crítica*, *39*:2. https://doi.org/10.1186/s41155-025-00369-8

Román Cortés, A. I. (2025). *An organisational cybernetics-based system for comprehensive academic performance evaluation in higher education* [Preprint]. SSRN. Centro de Integración Ingeniería y Sociedad, Facultad de Ingeniería, Universidad de Santiago de Chile.

**Documentos institucionales del proyecto (FING-USACH, 2026):**

- *Consentimiento Informado Entrevistas FING USACH* [Documento interno].
- *Manual de Evaluación y Calificación del Desempeño Académico de la Facultad de Ingeniería* [Borrador de resolución, V2].
- *Propuesta_Instrumento_Comisiones_Evaluadoras* [Informe técnico de instrumento].
- *Protocolo de Entrevista Académico* [Instrumento de entrevista].
- *Protocolo de Entrevista Comisión* [Instrumento de entrevista].
- *Protocolo de Entrevista Director* [Instrumento de entrevista].
- *Reporte Análisis Temático Entrevistas* [Informe de análisis, Fases 1–6, Braun y Clarke].
- *Reporte de resultados: Consulta diagnóstica sobre el proceso de evaluación y calificación del desempeño académico en la Facultad de Ingeniería* [Reporte de consulta 2026].
- *Fuentes evidencias* [Síntesis documental de fuentes de evidencia por área académica].
- Resolución N.º 5949 de 2009 (Universidad de Santiago de Chile), que regula el proceso de evaluación y calificación del desempeño académico.
- Decreto Universitario N.º 26 de 1986 (Universidad de Santiago de Chile), Reglamento de Carrera Académica.

---

## Anexo. Índice de archivos del repositorio

| Archivo | Tipo | Rol |
|---|---|---|
| `Reporte Analisis Tematico Entrevistas.pdf` | Evidencia primaria | Análisis temático de 4 entrevistas (Braun y Clarke, 2006) |
| `reporte_resultados_consulta_academicos_FING_Final.pdf` | Evidencia primaria | Consulta a 55 académicos, 10 unidades |
| `Propuesta_Instrumento_Comisiones_Evaluadoras.pdf` | Instrumento | Post-test de comisiones evaluadoras (15 Likert + 2 abiertas) |
| `PROTOCOLO DE ENTREVISTA ACADEMICO.docx` / `COMISION.docx` / `director.docx` | Instrumento | Protocolos de entrevista semiestructurada |
| `Consentimiento_Informado_Entrevistas_FING_USACH.docx` | Ético | Consentimiento informado |
| `fuentes evidencias.docx` | Síntesis | Fuentes de evidencia por área académica |
| `V2_ManualBorradorResolucion.docx` | Normativo | Borrador del Manual (62 artículos, 10 títulos) |
| `analisis_evaluacion_desempeno_FING.md` | Análisis | Diagnóstico institucional (250 palabras) |
| `lineas_accion_ajuste_hipotesis.md` | Análisis | Tres líneas de acción (150 palabras c/u) |
| `propuesta_art35_funcion_horas.md` | Propuesta normativa | Línea de acción 1 (Art. 35, 36) |
| `propuesta_trayectorias_maternidad.md` | Propuesta normativa | Línea de acción 2 (Art. 23, 25, 34) |
| `formato_convenio_desempeno.md` | Diseño | Especificación del CDA |
| `sistema_deliberacion_estructura.md` | Diseño técnico | Estructura de hojas de Google Sheets |
| `IMPLEMENTACION_GOOGLE_SHEETS.md` | Guía | Implementación paso a paso |
| `manual_desempeno_especificacion_editorial_CORREGIDA.md` | Especificación técnica | Reconstrucción programática del manual SVG |
| `Manual_Evaluacion_prototipo_30_limpio.svg` | Manual | Manual de 30 páginas, reparado (Fases A–E) |
| `avance_manual.svg` | Manual | Versión de avance del manual |
| `convenio_desempeno_maqueta.html` | Maqueta | Convenio de Desempeño Académico |
| `informe_actividades_maqueta.html` | Maqueta | Informe Anual de Actividades |
| `sistema_evaluacion_maqueta.html` / `_v2.html` | Maqueta | Sistema de evaluación por comisión |
| `apps_script_deliberacion.gs` | Backend | Google Apps Script (consolidación) |
| `panel_deliberacion.html` | Maqueta | Panel de deliberación independiente |
| `ejemplo_datos_deliberacion.json` | Datos de prueba | Caso ficticio para probar el panel |
| `s41155-025-00369-8.pdf` | Literatura | Rodrigues et al. (2026), SQPAE |
| `ssrn-5867602.pdf` | Literatura | Román Cortés (2025), VSM aplicado a evaluación académica |

---

*Fin del informe.*
