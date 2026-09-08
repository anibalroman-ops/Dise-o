/* ========================================================================
   GOOGLE APPS SCRIPT para Sistema de Deliberación USACH
   Recibe POST de maqueta HTML y escribe evaluaciones en Google Sheets
   ======================================================================== */

// Configuración
const SHEET_NAME_DATOS = "Datos brutos";
const SHEET_NAME_CONSOLIDACION = "Consolidación";
const SHEET_NAME_DELIBERACION = "Deliberación";
const SHEET_NAME_RESULTADO = "Resultado Final";

// ========================================================================
// ENDPOINT: recibe POST de la maqueta
// ========================================================================
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();

    // Validar que tenemos datos
    if (!payload.comisionado || !payload.evaluaciones) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: "Datos incompletos"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Escribir en hoja "Datos brutos"
    const sheet = ss.getSheetByName(SHEET_NAME_DATOS);
    const row = construirFila(payload);
    sheet.appendRow(row);

    // Actualizar hojas derivadas
    actualizarConsolidacion(ss, payload);

    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      message: "Evaluación registrada",
      timestamp: payload.timestamp
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ========================================================================
// Construir fila para "Datos brutos"
// ========================================================================
function construirFila(payload) {
  const com = payload.comisionado;

  // El académico puede no haber ejecutado alguna actividad comprometida:
  // en ese caso el sistema de evaluación excluye esa área del envío, y
  // "evals" llega con menos de 7 elementos. Se indexa por nombre (no por
  // posición) para que cada área siempre caiga en su columna fija del
  // encabezado, dejando en blanco la que no fue evaluada.
  const evalsPorNombre = {};
  payload.evaluaciones.areas.forEach(a => { evalsPorNombre[a.nombre] = a; });

  // Encabezado base: Timestamp, Comisionado, Email, Unidad, Tipo, Calidad
  const fila = [
    payload.timestamp,
    com.nombre,
    com.correo,
    com.unidad,
    com.tipo,
    com.calidad
  ];

  // Agregar nivel + fundamento + retroalimentación para cada una de las 7
  // áreas, en el orden fijo de AREAS_ORDEN (columnas siempre alineadas
  // con el encabezado, aunque falte alguna área en el envío).
  AREAS_ORDEN.forEach(nombreArea => {
    const area = evalsPorNombre[nombreArea];
    fila.push(area ? area.nivel : "");
    fila.push(area ? area.fundamento : "");
    fila.push(area ? area.retroalimentacion : "");
  });

  // Tiempo total y checks
  fila.push(payload.evaluaciones.tiempo_evaluacion);
  fila.push(payload.evaluaciones.comprende_horas ? "Sí" : "No");
  fila.push(payload.evaluaciones.comprende_circunstancias ? "Sí" : "No");

  // Incidentes (concatenados)
  const incidentes = payload.evaluaciones.incidentes
    .map(inc => `[${inc.tipo}] ${inc.texto}`)
    .join(" | ");
  fila.push(incidentes || "Sin incidentes");

  return fila;
}

// ========================================================================
// Actualizar hoja "Consolidación" (cálculos automáticos)
// ========================================================================
function actualizarConsolidacion(ss, payload) {
  const sheet = ss.getSheetByName(SHEET_NAME_CONSOLIDACION);

  // Limpiar y reconstruir
  if (sheet.getLastRow() > 1) {
    sheet.deleteRows(2, sheet.getLastRow() - 1);
  }

  // Obtener todas las evaluaciones de "Datos brutos"
  const datosSheet = ss.getSheetByName(SHEET_NAME_DATOS);
  const allData = datosSheet.getRange(2, 1, datosSheet.getLastRow() - 1, datosSheet.getLastColumn()).getValues();

  if (allData.length === 0) return;

  let fila = 2;

  // Por cada área
  const AREAS = [
    "Docencia", "Investigación y desarrollo", "Extensión - VIME",
    "Extensión - Educación continua", "Asistencia técnica",
    "Administración académica", "Perfeccionamiento"
  ];

  AREAS.forEach((area, idx) => {
    // Encabezado de área
    sheet.getRange(fila, 1).setValue(`═══ ${area} ═══`);
    sheet.getRange(fila, 1).setFontWeight("bold");
    sheet.getRange(fila, 1).setBackground("#E3F2FD");
    fila++;

    // Extraer evaluaciones para esta área
    const evaluaciones = allData.map((row, rowIdx) => ({
      comisionado: row[1],
      nivel: row[6 + idx * 3], // Columna de nivel para esta área
      fundamento: row[6 + idx * 3 + 1],
      retroalimentacion: row[6 + idx * 3 + 2],
      rowNum: rowIdx + 2
    }));

    // Mostrar lado a lado
    evaluaciones.forEach((e, i) => {
      sheet.getRange(fila, 1).setValue(`Comisionado ${i + 1}: ${e.comisionado}`);
      sheet.getRange(fila, 2).setValue(`Nivel: ${e.nivel}`);
      sheet.getRange(fila, 3).setValue(e.fundamento);
      fila++;
    });

    // Cálculo de divergencia
    const niveles = evaluaciones.map(e => e.nivel).filter(n => n !== "");
    const minN = Math.min(...niveles);
    const maxN = Math.max(...niveles);
    const divergencia = maxN - minN;

    const estado = divergencia === 0 ? "Consenso total" :
                   divergencia === 1 ? "Consenso moderado" :
                   "Discrepancia significativa";

    sheet.getRange(fila, 1).setValue(`Divergencia: ${estado} (máx-mín = ${divergencia})`);
    sheet.getRange(fila, 1).setFontStyle("italic");
    sheet.getRange(fila, 1).setBackground(divergencia > 1 ? "#FFECB3" : "#C8E6C9");
    fila += 2; // Espacio entre áreas
  });
}

// ========================================================================
// Inicializar hojas (ejecutar una sola vez desde el editor)
// ========================================================================
function inicializarHojas() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. "Datos brutos" - tabla donde llegan los datos
  crearHojaDatos(ss);

  // 2. "Consolidación" - se llena automáticamente
  crearHojaConsolidacion(ss);

  // 3. "Deliberación" - se edita manualmente
  crearHojaDeliberacion(ss);

  // 4. "Resultado Final" - resumen automático
  crearHojaResultado(ss);

  Logger.log("Hojas inicializadas correctamente");
}

function crearHojaDatos(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME_DATOS);
  if (sheet) sheet.clear();
  else sheet = ss.insertSheet(SHEET_NAME_DATOS);

  const headers = [
    "Timestamp", "Comisionado", "Email", "Unidad", "Tipo", "Calidad",
    "Docencia (Nivel)", "Docencia (Fund)", "Docencia (Retro)",
    "I+D (Nivel)", "I+D (Fund)", "I+D (Retro)",
    "Extensión-VIME (Nivel)", "Extensión-VIME (Fund)", "Extensión-VIME (Retro)",
    "Extensión-EdCont (Nivel)", "Extensión-EdCont (Fund)", "Extensión-EdCont (Retro)",
    "Asistencia Técnica (Nivel)", "Asistencia Técnica (Fund)", "Asistencia Técnica (Retro)",
    "Admin Académica (Nivel)", "Admin Académica (Fund)", "Admin Académica (Retro)",
    "Perfeccionamiento (Nivel)", "Perfeccionamiento (Fund)", "Perfeccionamiento (Retro)",
    "Tiempo Total", "Entiende Horas", "Entiende Circunstancias", "Incidentes"
  ];

  sheet.appendRow(headers);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, headers.length).setBackground("#1F2937").setFontColor("white").setFontWeight("bold");
}

function crearHojaConsolidacion(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME_CONSOLIDACION);
  if (sheet) sheet.clear();
  else sheet = ss.insertSheet(SHEET_NAME_CONSOLIDACION);

  sheet.appendRow(["CONSOLIDACIÓN DE EVALUACIONES — Lado a lado"]);
  sheet.getRange(1, 1).setFontSize(14).setFontWeight("bold").setBackground("#4F46E5").setFontColor("white");
  sheet.appendRow(["Se actualiza automáticamente al recibir evaluaciones."]);
  sheet.getRange(2, 1).setFontStyle("italic").setFontColor("#666");
}

function crearHojaDeliberacion(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME_DELIBERACION);
  if (sheet) sheet.clear();
  else sheet = ss.insertSheet(SHEET_NAME_DELIBERACION);

  sheet.appendRow(["PANEL DE DELIBERACIÓN — Discusión y decisión conjunta"]);
  sheet.getRange(1, 1).setFontSize(14).setFontWeight("bold").setBackground("#10B981").setFontColor("white");
  sheet.appendRow(["Completen esta hoja juntos. Para cada área:"]);
  sheet.appendRow(["1. Lean las 3 evaluaciones (lado a lado, en 'Consolidación')"]);
  sheet.appendRow(["2. Anoten sus argumentos abajo"]);
  sheet.appendRow(["3. Seleccionen el nivel acordado"]);
  sheet.appendRow(["4. Repitan para las 7 áreas"]);
  sheet.appendRow([""]);
  sheet.appendRow(["Nota: No existe tiempo límite. Deliberen hasta consenso o voto mayoritario."]);
}

function crearHojaResultado(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME_RESULTADO);
  if (sheet) sheet.clear();
  else sheet = ss.insertSheet(SHEET_NAME_RESULTADO);

  sheet.appendRow(["RESULTADO FINAL — Generado tras deliberación"]);
  sheet.getRange(1, 1).setFontSize(14).setFontWeight("bold").setBackground("#F59E0B").setFontColor("white");
  sheet.appendRow(["Este resumen se completa DESPUÉS de la deliberación."]);
  sheet.appendRow([""]);
  sheet.appendRow(["Información del académico:"]);
  sheet.appendRow(["Nombre:", "", "Unidad:", "", "Jerarquía:", "", "Período:", ""]);
  sheet.appendRow([""]);
  sheet.appendRow(["Resultado por área:"]);
  sheet.appendRow(["Área", "Eval. 1", "Eval. 2", "Eval. 3", "ACUERDO"]);

  const AREAS = [
    "Docencia", "Investigación y desarrollo", "Extensión - VIME",
    "Extensión - Educación continua", "Asistencia técnica",
    "Administración académica", "Perfeccionamiento"
  ];

  AREAS.forEach(area => {
    sheet.appendRow([area, "", "", "", ""]);
  });

  sheet.appendRow([""]);
  sheet.appendRow(["CALIFICACIÓN FINAL (Art. 35):"]);
  sheet.appendRow(["Suma ponderada:", ""]);
  sheet.appendRow(["Nivel:", ""]);
  sheet.appendRow([""]);
  sheet.appendRow(["Observaciones de la comisión:", ""]);
}

// ========================================================================
// Deploy function: ejecutar esta para obtener URL pública
// ========================================================================
function deploy() {
  // Esta función es solo una nota de referencia: no hace falta ejecutarla.
  // El despliegue real se hace desde el botón "Implementar" del editor
  // (arriba a la derecha) > "Nueva implementación" > tipo "Aplicación web".
  // La URL resultante es la que se pega en GOOGLE_APPS_SCRIPT_URL del HTML.
  Logger.log("Use el botón 'Implementar' del editor para desplegar, no esta función.");
}

// ========================================================================
// Datos del académico evaluado en este piloto.
// Ajuste estos valores si cambia el caso (deben coincidir con el objeto
// AREAS de sistema_evaluacion_maqueta_v2.html: mismo nombre, jornada y
// horas comprometidas por área, para que la calificación final coincida).
// ========================================================================
const ACADEMICO = {
  nombre: "Nombre Apellido Apellido",
  unidad: "Depto. de Ingeniería Industrial",
  jerarquia: "Profesor Asociado",
  periodo: "2026",
  jornada: 44,
  areas_horas: {
    "Docencia": 14,
    "Investigación y desarrollo": 10,
    "Extensión - VIME": 4,
    "Extensión - Educación continua": 3,
    "Asistencia técnica": 3,
    "Administración académica": 7,
    "Perfeccionamiento": 3
  }
};

const AREAS_ORDEN = [
  "Docencia", "Investigación y desarrollo", "Extensión - VIME",
  "Extensión - Educación continua", "Asistencia técnica",
  "Administración académica", "Perfeccionamiento"
];

// ========================================================================
// Generar el JSON que carga panel_deliberacion.html, a partir de las
// evaluaciones ya guardadas en "Datos brutos".
// ========================================================================
function generarJSONDeliberacion() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME_DATOS);
  const nFilas = sheet.getLastRow() - 1;

  if (nFilas <= 0) {
    SpreadsheetApp.getUi().alert("No hay evaluaciones en 'Datos brutos' todavía.");
    return;
  }

  const filas = sheet.getRange(2, 1, nFilas, sheet.getLastColumn()).getValues();

  const evaluaciones = filas.map(fila => {
    const areas = AREAS_ORDEN.map((nombre, idx) => {
      const base = 6 + idx * 3; // 0-indexado: col 7 = Docencia (Nivel)
      return {
        nombre: nombre,
        nivel: fila[base],
        fundamento: fila[base + 1]
      };
    }).filter(a => a.nivel !== "" && a.nivel !== null && a.nivel !== undefined);

    return {
      timestamp: fila[0] instanceof Date ? fila[0].toISOString() : String(fila[0]),
      comisionado: {
        nombre: fila[1],
        correo: fila[2],
        unidad: fila[3]
      },
      areas: areas
    };
  });

  const resultado = { academico: ACADEMICO, evaluaciones: evaluaciones };
  const json = JSON.stringify(resultado, null, 2);

  let hojaExport = ss.getSheetByName("Exportar JSON");
  if (!hojaExport) hojaExport = ss.insertSheet("Exportar JSON");
  hojaExport.clear();
  hojaExport.getRange(1, 1).setValue(
    "Haga doble clic en la celda de abajo, Ctrl+A (seleccionar todo dentro de la celda), Ctrl+C (copiar), y pegue el contenido en un archivo de texto nuevo guardado con extensión .json"
  ).setFontWeight("bold");
  hojaExport.getRange(2, 1).setValue(json).setWrap(true);
  ss.setActiveSheet(hojaExport);

  SpreadsheetApp.getUi().alert(
    "JSON generado en la hoja 'Exportar JSON', celda A2. Cópielo y péguelo en un archivo .json para subirlo al panel de deliberación."
  );
}

// ========================================================================
// Menú personalizado: aparece en la planilla al abrirla (puede tardar
// unos segundos la primera vez, o requerir refrescar la página una vez
// guardado este script).
// ========================================================================
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Deliberación")
    .addItem("Generar JSON para panel de deliberación", "generarJSONDeliberacion")
    .addToUi();
}
