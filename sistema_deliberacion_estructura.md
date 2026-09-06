# Sistema de Deliberación — Estructura Google Sheets

## Flujo General

1. **Comisionado 1, 2, 3** evalúan en maqueta HTML → botón "Enviar evaluación"
2. Datos POST a Google Apps Script
3. Apps Script escribe en Sheets "Datos brutos"
4. Hoja "Consolidación" se llena automáticamente con fórmulas
5. Ustedes se juntan en hoja "Deliberación" y deciden nivel final
6. Hoja "Resultado" genera PDF descargable

---

## Estructura de Hojas

### Hoja 1: "Datos brutos"
Recibe automáticamente los datos de cada comisionado. Columnas:

| Timestamp | Comisionado | Email | Unidad | Jerarquía | Docencia (N) | Docencia (Fund) | I+D (N) | I+D (Fund) | Extensión-VIME (N) | ... | Perfeccionamiento (N) | Perfeccionamiento (Fund) |
|-----------|------------|-------|--------|-----------|--------------|-----------------|--------|------------|-------------------|-----|------------------------|-----------------------|

Una fila por evaluador. Las filas se agregan automáticamente desde Apps Script.

---

### Hoja 2: "Consolidación"
**Muestra lado a lado las 3 evaluaciones por área.**

Estructura (ejemplo para Docencia):

```
ÁREA: DOCENCIA
════════════════════════════════════════════════════════════════════

Comisionado 1                Comisionado 2                Comisionado 3
Nombre: [auto]               Nombre: [auto]               Nombre: [auto]
Nivel: 3 (Bueno)             Nivel: 4 (Sobresaliente)     Nivel: 3 (Bueno)
Fundamento:                  Fundamento:                  Fundamento:
"Cumple plenamente... [auto] "Supera verificablemente... [auto] "Cumple plenamente... [auto]
```

**Divergencia calculada:** ¿Hay consenso o discrepancia?
- Si max-min ≤1: "Consenso moderado"
- Si max-min >1: "Discrepancia significativa — requiere deliberación"

---

### Hoja 3: "Deliberación"
**Panel colaborativo para discusión y decisión final.**

Estructura por área (repetida para todas):

```
╔═══════════════════════════════════════════════════════════════════╗
║ ÁREA: DOCENCIA (14 h comprometidas · 36% de jornada)              ║
╚═══════════════════════════════════════════════════════════════════╝

Evaluaciones individuales:
  • Comisionado 1: Nivel 3 (Bueno)
  • Comisionado 2: Nivel 4 (Sobresaliente)
  • Comisionado 3: Nivel 3 (Bueno)

Divergencia: Discrepancia significativa (máx-mín = 1)

───────────────────────────────────────────────────────────────────
DELIBERACIÓN EN VIVO
───────────────────────────────────────────────────────────────────

Notas de la comisión:
[CAMPO EDITABLE: aquí anotan su discusión]

Argumentos principales:
□ Cumplimiento consistente
□ Brechas relevantes
□ Aportes verificables adicionales
□ Otras circunstancias

DECISIÓN FINAL:
  Nivel acordado: [SELECTOR 0-4]
  Fecha/Hora decisión: [AUTO con fecha]
  Comisionado que registra: [SELECTOR]

───────────────────────────────────────────────────────────────────
```

Repite esta estructura para las 7 áreas.

---

### Hoja 4: "Resultado Final"
**Resumen ejecutivo con CF final.**

```
╔═══════════════════════════════════════════════════════════════════╗
║ RESULTADO FINAL DE LA EVALUACIÓN — DELIBERACIÓN CONJUNTA          ║
╚═══════════════════════════════════════════════════════════════════╝

Académico: Nombre Apellido Apellido
Unidad: Depto. de Ingeniería Industrial
Jerarquía: Profesor Asociado
Período: 2026

────────────────────────────────────────────────────────────────────
RESULTADO POR ÁREA
────────────────────────────────────────────────────────────────────

Área                          H. Compromet. Eval. 1 Eval. 2 Eval. 3 ACUERDO
═════════════════════════════════════════════════════════════════════════
Docencia                      14 (36%)       3       4       3       3
Investigación y desarrollo    10 (25%)       3       3       3       3
Extensión - VIME              4  (10%)       2       2       2       2
Extensión - Educación         3  (8%)        3       3       3       3
Asistencia técnica            3  (8%)        0       0       0       0
Administración académica      7  (18%)       3       3       3       3
Perfeccionamiento             3  (8%)        4       4       4       4
════════════════════════════════════════════════════════════════════════

CALIFICACIÓN FINAL (Art. 35):
═══════════════════════════════════════════════════════════════════════
Suma ponderada (niveles × horas):
  (3×14 + 3×10 + 2×4 + 3×3 + 0×3 + 3×7 + 4×3) / 44 = 2.95

NIVEL FINAL: 3 (Bueno)

────────────────────────────────────────────────────────────────────
OBSERVACIONES DE LA COMISIÓN
────────────────────────────────────────────────────────────────────
[Texto libre: síntesis de la deliberación, decisiones especiales, etc.]

────────────────────────────────────────────────────────────────────
FIRMA ELECTRÓNICA
────────────────────────────────────────────────────────────────────
Comisionado 1: __________ Fecha: __________
Comisionado 2: __________ Fecha: __________
Comisionado 3: __________ Fecha: __________

Registro generado: [TIMESTAMP AUTO]
```

---

## Datos que envía la maqueta

Cuando el comisionado hace clic en "Enviar evaluación":

```json
{
  "timestamp": "2026-09-06T14:30:45Z",
  "comisionado": {
    "nombre": "Dr. Juan Pérez",
    "correo": "juan.perez@usach.cl",
    "unidad": "Depto. Ingeniería Informática",
    "tipo": "Director",
    "calidad": "Titular"
  },
  "evaluaciones": {
    "areas": [
      {
        "nombre": "Docencia",
        "nivel": 3,
        "fundamento": "Cumple plenamente lo esperado para la jerarquía...",
        "retroalimentacion": "Fortalezas: autonomía en conducción..."
      },
      {
        "nombre": "Investigación y desarrollo",
        "nivel": 3,
        "fundamento": "...",
        "retroalimentacion": "..."
      },
      ... (7 áreas)
    ],
    "tiempo_evaluacion": "00:45:32",
    "comprende_horas": true,
    "comprende_circunstancias": true,
    "incidentes": [
      {"tipo": "Duda de criterio", "texto": "...", "hora": "14:20"}
    ]
  }
}
```

Apps Script recibe esto y lo expande en fila de "Datos brutos".

---

## Instrucciones para Implementación

### Paso 1: Crear Google Sheet
1. Ir a https://sheets.google.com
2. Nueva hoja
3. Crear hojas: "Datos brutos", "Consolidación", "Deliberación", "Resultado Final"

### Paso 2: Copiar Apps Script
1. Menú > Extensiones > Apps Script
2. Copiar código del archivo `apps_script_deliberacion.gs` (adjunto)
3. Guardar como proyecto
4. Copiar URL del deployment (aparece en pantalla)

### Paso 3: Integrar maqueta v2
1. Actualizar `sistema_evaluacion_maqueta_v2_deliberacion.html`
2. Reemplazar `GOOGLE_APPS_SCRIPT_URL` con la URL del paso 2
3. Probar: evaluar, clic en "Enviar" → datos deben aparecer en Sheets

### Paso 4: Deliberación
1. Ver "Consolidación": verán lado a lado las 3 evaluaciones
2. Ir a "Deliberación": anotan discusión, deciden nivel final
3. "Resultado Final" se llena automáticamente

---

## Seguridad & Privacidad

- Apps Script corre en cuenta Google del usuario (USACH)
- Datos solo en Google Sheets (no en internet público)
- Acceso: solo la comisión + secretaría técnica (comparten link)
- Cada evaluación tiene timestamp y quién la envió
- Deliberación queda registrada para auditoría (Art. 52, Título IX)
