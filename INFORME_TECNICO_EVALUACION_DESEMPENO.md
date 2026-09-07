# Informe técnico — Proceso de evaluación y calificación del desempeño académico

**Facultad de Ingeniería, Universidad de Santiago de Chile (FING-USACH)**
**Período cubierto:** agosto 2026 – 7 de septiembre de 2026
**Repositorio:** `anibalroman-ops/Dise-o`, rama `claude/inkscape-automation-scripts-3nrjdj`
**Elaborado por:** asistencia técnica Claude Code, a partir del historial de trabajo y la documentación del repositorio

---

## 1. Resumen ejecutivo

Entre agosto y septiembre de 2026 se desarrolló, en ocho etapas encadenadas, un proceso de rediseño técnico y normativo del sistema de evaluación del desempeño académico de la FING-USACH. El trabajo partió de una base empírica levantada en agosto (entrevistas, análisis temático y consulta a académicos) y avanzó en septiembre hacia: (a) la reparación editorial de un manual normativo de 30 páginas diseñado en SVG; (b) un análisis institucional restringido a las fuentes documentales del proyecto; (c) tres líneas de acción normativas para ajustar las hipótesis del rediseño; (d) la redacción de artículos concretos para dos de esas líneas; (e) tres maquetas HTML funcionales (Convenio de Desempeño Académico, Informe Anual de Actividades y Sistema de Evaluación por comisión); (f) una integración con Google Sheets para consolidar evaluaciones de tres comisionados; y (g) un panel HTML independiente de deliberación conjunta, con corrección iterativa de errores y mejoras de usabilidad hasta el 7 de septiembre.

El resultado es un **piloto operativo end-to-end**, listo para probarse con un caso real: un académico evalúa un caso, tres comisionados completan el formulario de evaluación, los datos se consolidan en Google Sheets, y la comisión delibera y decide en el panel HTML, que calcula automáticamente la calificación final ponderada (Art. 35) y genera un acta firmable.

---

## 2. Insumos previos (agosto 2026)

Antes del desarrollo registrado en el repositorio (que comienza el 4 de septiembre), el proyecto contaba con una base empírica y documental levantada en agosto 2026, incorporada al repositorio el 5 de septiembre como material de trabajo:

| Documento | Rol en el proyecto |
|---|---|
| `PROTOCOLO DE ENTREVISTA ACADEMICO.docx`, `PROTOCOLO DE ENTREVISTA COMISION.docx`, `PROTOCOLO DE ENTREVISTA director.docx` | Instrumentos de entrevista semiestructurada aplicados a académicos, comisionados y al Vicedecanato/dirección. |
| `Consentimiento_Informado_Entrevistas_FING_USACH.docx` | Consentimiento informado para la recolección de entrevistas. |
| `Reporte Analisis Tematico Entrevistas.pdf` | Análisis temático (Braun y Clarke) de cuatro entrevistas. |
| `reporte_resultados_consulta_academicos_FING_Final.pdf` | Consulta a académicos: 55 respuestas sobre una población de 180. |
| `Propuesta_Instrumento_Comisiones_Evaluadoras.pdf` | Instrumento de 15 ítems Likert + 2 preguntas abiertas para comisiones evaluadoras (post-test de evaluadores, previsto para el piloto). |
| `fuentes evidencias.docx` | Sistematización de fuentes de evidencia usadas en el diagnóstico. |
| `V2_ManualBorradorResolucion.docx` | Borrador normativo de referencia del Manual de Evaluación (62 artículos). |
| `JornadaAcademicos.pptx`, `Plan de validación y pilotaje - cronograma.pptx` | Presentaciones de contexto y cronograma de validación/pilotaje. |
| `evaluacion_academica_piloto_consolidado.zip`, `index (11).html` | Consolidado de piloto y visor HTML asociado. |
| `s41155-025-00369-8.pdf`, `ssrn-5867602.pdf` | Literatura académica de referencia citada en el diagnóstico. |

Esta base es la que se cita en el análisis institucional (sección 4) con cifras como "55 respuestas sobre 180" o "63,6% desacuerda con que hoy se valore calidad más allá de horas".

---

## 3. Fase 0 — Infraestructura de automatización (4 de septiembre)

**Commit:** `1a13172` — *Add PowerShell + VS Code automation toolkit for Inkscape diagrams*

Se construyó un conjunto de scripts de PowerShell para generar y exportar en lote diagramas diseñados en Inkscape, integrado como tareas de VS Code:

- `scripts/ps/New-FromTemplate.ps1` — combina una plantilla SVG (con ids por elemento) y un JSON de datos para generar un diagrama.
- `scripts/ps/Export-Diagram.ps1` / `Export-AllDiagrams.ps1` — exportación individual y en lote a PDF/PNG.
- `scripts/ps/Invoke-InkscapeAction.ps1` — ejecución de acciones arbitrarias de Inkscape (mover, alinear, cambiar color por id) desde la línea de comandos.
- `templates/informe_basico.svg`, `data/ejemplo_informe.json`, `docs/inkscape-cli-referencia.md`, `config/inkscape.config.json`, `.vscode/tasks.json` — plantilla de ejemplo, referencia de comandos, configuración y tareas de un clic.

Esta infraestructura fue la base técnica que permitió, después, editar programáticamente el SVG del manual (fase 1).

---

## 4. Fase 1 — Reparación editorial del Manual de Evaluación (SVG, 4–5 de septiembre)

**Archivo intervenido:** `Manual_Evaluacion_prototipo_30_limpio.svg` (30 páginas, formato A4, 10 Títulos normativos).

El manual presentaba errores estructurales heredados de su diseño original en Inkscape. Se corrigió en cinco fases secuenciales:

| Fase | Commit | Corrección |
|---|---|---|
| **A** | `e2faf39` | `viewBox` multipágina roto, casos de color inconsistentes, texto vacío o corrupto, superposición de títulos. |
| **B** | `d3556ea` | Normalización de la escala tipográfica: de 76 tamaños de fuente distintos a un sistema de ~10, con mínimo de 8 pt legible. |
| **C** | `90afb18`, `2db34b0` | Colisiones de contenido con el pie de página en 8 páginas (04, 06, 12, 14, 19, 24, 27, 28), resueltas por compresión vertical por tramos; corrección de regresiones residuales (líneas de pie y bordes de tarjetas). |
| **D** | `1af0e15`, `e508308` | Reparación de un componente de flujo de pasos roto y limpieza de fragmentos de ícono/texto duplicados o huérfanos (páginas 10, 11, 12, 15, 18, 27). |
| **E** | `cf1e1b5` | Títulos y texto cortado o superpuesto en las páginas 27 y 28, con verificación final de las 30 páginas. |

Posteriormente se incorporó una versión de avance más extensa del manual (`avance_manual.svg`, commit `3fcf151`) y su especificación editorial normalizada, `manual_desempeno_especificacion_editorial_CORREGIDA.md` (commit `8e31056`): un documento de especificación técnica (formato A4 210×297 mm, tipografía Noto Sans/Noto Serif Display, texto editable como `<text>/<tspan>`, sin curvas) pensado como fuente única para reconstrucción programática del manual en Inkscape, con reglas explícitas de precedencia sobre el orden de páginas, la corrección de desbordes y la prohibición de residuos duplicados.

---

## 5. Fase 2 — Análisis institucional bajo restricción de fuentes (5 de septiembre)

**Commit:** `bc39bce` — **Archivo:** `analisis_evaluacion_desempeno_FING.md`

Por instrucción expresa, este análisis se elaboró bajo una restricción metodológica estricta: sin recurrir a internet ni a memoria externa a la conversación, usando únicamente las fuentes documentales cargadas en el repositorio (sección 2). El resultado es un párrafo de exactamente 250 palabras que sintetiza el diagnóstico institucional. Sus hallazgos centrales:

- El proyecto **triangula** revisión documental, cuatro entrevistas (Braun y Clarke) y una consulta de 55/180 respuestas.
- Sus productos (manual de 62 artículos, rúbrica holística 0–4, prototipo web) fueron declarados explícitamente **hipótesis, no soluciones**.
- **Asimetría central:** el diagnóstico está mejor validado que la propuesta; la validación experta y el piloto operativo seguían pendientes al momento del análisis.
- **Ninguna de las seis dimensiones evaluadas alcanza media 3,0**, pero los tres criterios del rediseño superan **83% de acuerdo**: la comunidad rechaza el proceso vigente y preaprueba los principios del manual nuevo.
- El nudo del rechazo es **gobernanza** (63,6%), asociado a objetividad, claridad y carga — no a la comprensión normativa.
- Tres riesgos identificados: (1) "condiciones institucionales" (70,9% de rechazo) excede el alcance de un manual que regula juicio y procedimiento, no recursos; (2) el Art. 35 mantiene las horas como ponderador aun cuando el nivel se juzga cualitativamente, riesgo de leerse como "simulación de cambio" si no se explicita; (3) maternidad y trayectorias biográficas, mencionadas en las entrevistas, no estaban operacionalizadas pese a ser la dimensión peor evaluada (media 2,15).
- Un 38,2% de los académicos **nunca fue evaluado**, señal de un proceso semiinactivo.

---

## 6. Fase 3 — Líneas de acción de ajuste de hipótesis (5 de septiembre)

**Commit:** `8b8c905` — **Archivo:** `lineas_accion_ajuste_hipotesis.md`

A partir del análisis anterior, se redactaron tres líneas de acción, cada una en exactamente 150 palabras:

1. **Artículo 35 y las horas.** Explicitar que las horas comprometidas (factor Pi) son un *ponderador* de dedicación, no una medida de desempeño; el nivel (Ni) proviene del juicio holístico de la rúbrica. Se cita el caso importado (2.070 h realizadas vs. 1.944 h comprometidas) como ilustración de que ambos valores deben mostrarse separados, nunca sumados.
2. **Trayectorias y maternidad.** Convertir el contexto biográfico (maternidad, licencias, inicio de carrera, cambios de jornada) en un **campo declarable, voluntario y confidencial** en el CDA, que ajuste el *volumen* de compromisos esperado sin alterar la *exigencia de calidad* ni la escala de evaluación.
3. **Diseño del piloto.** Reconvertir el piloto para que pruebe no solo el sistema, sino también las dos hipótesis anteriores: aprovechar que el caso real importado genera tres evaluaciones independientes (A-001-2023, 2024, 2025); agregar mediciones de divergencia entre evaluadores, calidad de fundamentación, y comprensión de la separación horas/nivel; y cerrar con el instrumento de 15 ítems Likert + 2 abiertas como post-test de los comisionados.

---

## 7. Fase 4 — Redacción normativa de las líneas de acción 1 y 2 (5 de septiembre)

Se tradujeron las líneas de acción 1 y 2 en propuestas concretas de párrafos normativos, listas para incorporarse al manual sin alterar la numeración de artículos existente.

### 7.1 Línea de acción 1 — Función de las horas (Art. 35 y 36)

**Commit:** `ad9b0b0` — **Archivo:** `propuesta_art35_funcion_horas.md`

- **Art. 35:** nuevo párrafo que fija que el factor Pi "opera exclusivamente como ponderador de la importancia relativa" y que el nivel Ni "provendrá siempre del juicio académico fundado de la comisión" sobre evidencia verificable, rol, jerarquía y alcance — nunca del cómputo de horas.
- **Art. 36:** nuevo párrafo que establece que la diferencia entre horas comprometidas y realizadas "no modificará por sí sola el nivel de desempeño"; ni exceder horas sube el nivel automáticamente, ni un déficit lo baja si la evidencia sostiene el cumplimiento. Si la diferencia es relevante, la comisión debe dejar constancia fundada en el expediente.
- Se identifican dos ajustes de consecuencia fuera de esta propuesta: una regla equivalente en el Anexo I (punto 5) y un requisito funcional en el Art. 57 para que la plataforma muestre nivel y ponderación en campos distintos.

### 7.2 Línea de acción 2 — Trayectorias, contextos y circunstancias (Art. 23, 25, 34)

**Commit:** `8e4b793` — **Archivo:** `propuesta_trayectorias_maternidad.md`

- **Art. 23:** incorpora una sección **voluntaria y confidencial** (Art. 52) de "circunstancias del período" (pre/postnatal, cuidados, licencias, inicio de carrera, cambios de jornada), cuyo único efecto es ajustar el volumen de compromisos al formalizar el CDA — sin afectar calidad, escala ni rúbrica. Solo la conocen el Director/a y la comisión; no entra en reportes agregados.
- **Art. 25:** permite solicitar modificación excepcional del CDA cuando estas circunstancias sobrevienen o se prolongan, con el mismo efecto acotado.
- **Art. 34:** obliga a la comisión a dejar constancia (sin detallar la naturaleza de la circunstancia) de que evaluó sobre el volumen ajustado, para evitar que el ajuste opere como criterio oculto; su omisión es reclamable (Art. 54).
- Ajustes de consecuencia identificados fuera de alcance: campo de acceso diferenciado en Art. 56/57, indicación en Anexos II/III sobre lectura de trayectorias con interrupciones, y verificación normativa de datos personales sensibles.

---

## 8. Fase 5 — Maquetas HTML funcionales (5–6 de septiembre)

Se construyeron tres maquetas HTML autocontenidas (sin dependencias externas), con un sistema de diseño común: paleta índigo (`#4F46E5`), header sticky, tarjetas con sombra, tipografía jerarquizada.

| Maqueta | Commit | Archivo | Función |
|---|---|---|---|
| Convenio de Desempeño Académico | `5537a93`, `77dab0c` | `convenio_desempeno_maqueta.html` | Formulario de compromisos anuales por área, según el diseño documentado en `formato_convenio_desempeno.md` (ver 8.1). |
| Informe Anual de Actividades | `10f2696` | `informe_actividades_maqueta.html` | Vista de reporte anual de actividades realizadas. |
| Sistema de Evaluación (comisión) | `e54d68a`, `b4e1632`, `bce3b90` | `sistema_evaluacion_maqueta.html` (v1) y `sistema_evaluacion_maqueta_v2.html` (v2) | Interfaz para que un comisionado evalúe un caso completo: identificación, antecedentes por área, juicio holístico 0–4, registro de tiempo e incidentes. La v2 agregó identificación obligatoria del comisionado (nombre, correo, unidad, titular/suplente, tipo) y un rediseño visual completo (header, stepper, tablas con franjas). |

### 8.1 Diseño del Convenio de Desempeño Académico

**Archivo:** `formato_convenio_desempeno.md` (commit `7a9e909`)

Documento de diseño previo a la maqueta HTML, con principios explícitos: una hoja de compromisos, la fila como unidad evaluable, "la ponderación pesa, no califica", el contexto se declara aparte (hoja reservada), y los datos de identificación se escriben una sola vez. Define estructura (A–F), contenido campo a campo, reglas de diagramación y cinco validaciones antes de formalizar (suma de ponderaciones = 100%, evidencia declarada por fila, mínimos normativos cubiertos, roles asociados, advertencia — no bloqueo — por exceso de compromisos).

### 8.2 Sistema de Evaluación v2 — estructura interna

`sistema_evaluacion_maqueta_v2.html` organiza el flujo en 3 pasos (identificación y conflicto de interés → antecedentes y evaluación por 7 áreas → registro de tiempo, incidentes y envío), con un modal de evaluación por área que incluye la Rúbrica General (escala 0–4: Insuficiente, Condicional, Aceptable, Bueno, Sobresaliente), fundamentación obligatoria (reforzada para niveles 0, 1 y 4) y una Guía Orientadora filtrada por jerarquía cuando existe (actualmente solo para Docencia e Investigación y Desarrollo). Calcula una vista preliminar de la calificación final (CF) como suma ponderada por horas comprometidas, explícitamente etiquetada como "preliminar y personal — no constituye la calificación final".

---

## 9. Fase 6 — Integración con Google Sheets (6 de septiembre)

**Commit:** `aebbf5b` — *Integración Google Sheets: evaluaciones → consolidación → deliberación*

Para el piloto (una comisión de exactamente 3 personas evaluando 1 caso), se optó por Google Sheets como backend sin servidor: cada comisionado completa la maqueta v2 y envía su evaluación por `fetch`/POST a un Google Apps Script.

**Archivos:**
- `apps_script_deliberacion.gs` — código del backend: `doPost(e)` recibe el payload JSON, lo valida, escribe una fila en la hoja "Datos brutos" y recalcula automáticamente la hoja "Consolidación" (las evaluaciones de los 3 comisionados lado a lado por área, con cálculo de divergencia — máx-mín — y semáforo de consenso). Incluye funciones de inicialización (`inicializarHojas`) que crean las cuatro hojas del libro: Datos brutos, Consolidación, Deliberación y Resultado Final.
- `sistema_deliberacion_estructura.md` — especificación de las 4 hojas, el formato exacto del payload JSON enviado desde la maqueta, y las reglas de seguridad y confidencialidad (Art. 52, Título IX): el Google Sheet es privado y compartido solo por enlace, cada evaluación queda con timestamp de auditoría.
- `IMPLEMENTACION_GOOGLE_SHEETS.md` — guía paso a paso (9 pasos) para que la Secretaría Técnica cree el Sheet, copie el Apps Script, lo despliegue como aplicación web, comparta la URL con los 3 comisionados y monitoree la llegada de datos; incluye sección de resolución de problemas.

En esta fase, la hoja "Deliberación" seguía pensada como un espacio de edición manual dentro del propio Google Sheets.

---

## 10. Fase 7 — Panel de deliberación HTML independiente (6–7 de septiembre)

Por decisión explícita del usuario ("en vez de que la comisión se junte a deliberar sobre la planilla, debe ser un sistema html... A este interfaz yo le debo subir la planilla"), se reemplazó la deliberación manual en Sheets por una interfaz HTML independiente, sin dependencias del backend de Sheets: recibe como entrada el JSON exportado desde la planilla consolidada.

**Archivo:** `panel_deliberacion.html` (commit `80cf658`, con iteraciones posteriores).

**Funcionalidad principal:**
- Carga de archivo JSON con las 3 evaluaciones y los datos del académico.
- **Cuadro resumen** por área (agregado en una iteración posterior, commit `1e3efd8`): tabla con las 7 áreas × 3 comisionados, badges de nivel por comisionado, estado de divergencia (Consenso total / moderado / Discrepancia) y columna de "Acordado" que se actualiza en vivo; contador de progreso "X/7 áreas decididas"; filas clickeables que saltan al detalle del área.
- Por cada área: evaluaciones lado a lado con fundamento citado, cálculo de divergencia (máx–mín), selector de nivel acordado (0–4) y notas de deliberación.
- Cálculo dinámico de la calificación final (CF, Art. 35) como suma ponderada por horas reales del académico.
- Panel de firmas de los 3 comisionados (Art. 52, Título IX) con hora de la evaluación original.
- Botón final que valida que las 7 (o menos, ver §11) áreas estén decididas y genera un JSON de resultado descargable con timestamp, deliberaciones, CF final y firmas.

Se generó además `ejemplo_datos_deliberacion.json` (commit `194ad2d`, revisado en iteraciones posteriores) como caso de prueba de un académico ficticio (Dr. Carlos Mendoza García) evaluado por 3 comisionados, para validar el sistema sin depender de datos reales de Sheets.

---

## 11. Fase 8 — Correcciones e iteraciones de calidad (6–7 de septiembre)

Tras la puesta en marcha del panel de deliberación surgieron errores y ajustes, corregidos iterativamente:

| Commit | Corrección |
|---|---|
| `8a3d36c`, `1a7b177` | Incompatibilidad de estructura entre el JSON de ejemplo y el código del panel (`e.evaluaciones.areas` vs. `e.areas`); se hizo el panel tolerante a ambas formas con *optional chaining*. |
| `338cca0` | **Bug de contraste en el botón de nivel seleccionado**: una regla CSS por atributo (`[data-n="3"]`) tenía la misma especificidad que la clase `.sel` pero se declaraba después, por lo que el texto azul del nivel ganaba sobre el blanco esperado, dejando el botón seleccionado casi ilegible sobre fondo índigo. Se corrigió usando el color semántico de cada nivel (rojo/naranja/gris/azul/verde) como fondo sólido al seleccionar. |
| `1e3efd8` | **Bug de cálculo real**: `calcularCF()` en el panel usaba un arreglo de horas *hardcodeado* (`[14,10,4,3,3,7,3]`) en vez de leer `areas_horas` del JSON cargado, por lo que la calificación final nunca reflejaba las horas reales del académico evaluado. Corregido para leer los datos reales. |
| `8b77079` | **Regla de negocio: áreas no ejecutadas no penalizan.** Si un académico comprometió una actividad en el CDA pero no la ejecutó durante el período (0 horas realizadas), esa área ya no se muestra para evaluación en `sistema_evaluacion_maqueta_v2.html` (no pide nivel 0–4, no bloquea el envío) y se excluye del cálculo ponderado de la CF, con una nota de transparencia visible para el comisionado. El mismo criterio se replicó en `panel_deliberacion.html`, que ahora calcula dinámicamente el conjunto de áreas aplicables (intersección de las áreas que los 3 comisionados efectivamente evaluaron) en vez de asumir una lista fija de 7, para no romperse cuando un académico tiene menos áreas aplicables. `ejemplo_datos_deliberacion.json` se actualizó para reflejar este caso (Asistencia técnica excluida). |

Cada corrección fue validada ejecutando la lógica extraída con Node.js antes de confirmar el fix (sintaxis del script, simulación de `calcularCF`, verificación de la exclusión de áreas), como control de calidad previo al commit.

---

## 12. Estado actual del sistema (al 7 de septiembre de 2026)

El piloto queda operativo de extremo a extremo:

1. **Convenio de Desempeño Académico** (`convenio_desempeno_maqueta.html`) — el académico compromete actividades por área.
2. **Informe Anual de Actividades** (`informe_actividades_maqueta.html`) — reporte de lo efectivamente realizado.
3. **Evaluación individual** (`sistema_evaluacion_maqueta_v2.html`) — cada uno de los 3 comisionados evalúa el caso de forma independiente y envía su resultado a Google Sheets.
4. **Consolidación automática** (`apps_script_deliberacion.gs` + Google Sheets) — las 3 evaluaciones se agrupan lado a lado con divergencia calculada.
5. **Deliberación conjunta** (`panel_deliberacion.html`) — la comisión carga el JSON exportado, ve el resumen por área, delibera, decide el nivel acordado por área y firma. El sistema calcula la calificación final (Art. 35) y genera el acta descargable.

Todo el trabajo está en la rama `claude/inkscape-automation-scripts-3nrjdj` del repositorio `anibalroman-ops/Dise-o`, sin pull request abierto a la fecha de este informe.

---

## 13. Pendientes identificados

A partir de las líneas de acción (sección 6) y del propio desarrollo, quedan pendientes explícitos:

- **Validación experta y piloto operativo real**, señalados como pendientes desde el análisis institucional (sección 4): el sistema está listo, pero no se ha ejecutado aún con un caso real y comisionados reales.
- **Instrumento de comisiones evaluadoras** (15 ítems Likert + 2 abiertas, `Propuesta_Instrumento_Comisiones_Evaluadoras.pdf`) — previsto como post-test de los evaluadores al cierre del piloto, aún no aplicado.
- **Mediciones adicionales del piloto** propuestas en la línea de acción 3: divergencia entre evaluadores antes de deliberar (el panel ya la calcula automáticamente), calidad de las fundamentaciones escritas, y verificación de que la separación horas/nivel y el ajuste por contexto fueron comprendidos por los comisionados.
- **Ajustes de consecuencia** identificados en las propuestas normativas (secciones 7.1 y 7.2) pero explícitamente fuera de su alcance: regla de lectura en el Anexo I, requisito funcional en el Art. 57 (mostrar nivel y ponderación en campos distintos en la plataforma), campo de acceso diferenciado para la declaración voluntaria (Art. 56/57), indicación en los Anexos II/III sobre lectura de trayectorias con interrupciones, y verificación frente a la normativa de datos personales sensibles.
- **Línea de acción 2** (trayectorias y maternidad) aún no tiene una implementación funcional en las maquetas HTML — la propuesta normativa (Art. 23, 25, 34) está redactada, pero el campo de "declaración voluntaria de circunstancias del período" no se ha incorporado como componente del Convenio de Desempeño Académico ni del sistema de evaluación.
- **Generación de PDF** del resultado final de la deliberación — actualmente el panel solo descarga el resultado en formato JSON.
- **Integración del resultado al expediente formal** del académico, mencionada como "próximo paso" en la pantalla de envío de la maqueta de evaluación, pero no implementada.

---

## 14. Índice de archivos relevantes del repositorio

| Archivo | Tipo | Rol |
|---|---|---|
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

---

*Fin del informe.*
