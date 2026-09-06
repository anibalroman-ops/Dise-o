# Implementación: Sistema de Evaluación + Google Sheets

## Resumen del Flujo

1. **Comisionados evalúan** en maqueta HTML (`sistema_evaluacion_maqueta_v2.html`)
2. **Cada uno envía** su evaluación a Google Sheets (vía Apps Script)
3. **Sheets consolida** automáticamente las 3 evaluaciones (lado a lado)
4. **Ustedes deliberan** en Sheets, anotan decisiones, firman
5. **Resultado final** se genera automáticamente (PDF descargable)

---

## PASO 1: Crear Google Sheet

1. Ir a https://sheets.google.com
2. Botón "+ Nuevo" → "Hoja de cálculo"
3. Nombre: `Evaluación Comisión FING 2026` (o similar)
4. Crear

---

## PASO 2: Crear Hojas

Borrá la hoja "Hoja 1" por defecto. Luego agregá 4 hojas nuevas (botón + abajo):

1. **"Datos brutos"** — recibe las evaluaciones automáticamente
2. **"Consolidación"** — muestra lado a lado
3. **"Deliberación"** — panel para discutir
4. **"Resultado Final"** — resumen ejecutivo

---

## PASO 3: Copiar Apps Script

1. En Google Sheets, botón ≡ (arriba a la izquierda) → **Extensiones** → **Apps Script**
2. Se abre pestaña nueva con editor de código
3. Borrá todo lo que hay por defecto
4. **Copiar completamente el archivo `apps_script_deliberacion.gs`** (adjunto)
5. Pegá en el editor
6. **Ctrl+S** para guardar (le pide nombre; acepta "proyecto1" o similar)

---

## PASO 4: Ejecutar Inicialización

1. Arriba del editor de Apps Script, selector de función: elige **`inicializarHojas`**
2. Botón ▶ (ejecutar)
3. Pide permisos: autorizá
4. Si todo va bien, aparece un popup: "Hojas inicializadas correctamente"
5. Volví a la pestaña de Google Sheets → refrescá F5
6. Deberías ver las 4 hojas con encabezados y estructuras

---

## PASO 5: Deploy (obtener URL pública)

1. En el editor Apps Script, selector de función: elige **`deploy`**
2. Botón ▶ (ejecutar)
3. Aparece popup con instrucciones
4. **Alternativamente, deploy manual:**
   - Botón "Implementar" (arriba a la derecha) → "Nueva implementación"
   - Tipo: "Aplicación web"
   - Parámetros:
     - Ejecutar como: **[Tu email]**
     - Quién tiene acceso: **"Cualquiera que tenga el enlace"**
   - Botón "Implementar"
   - Se abre popup con **URL de implementación**
   - **COPIAR ESTA URL** ← esto es lo que necesitas

**Ejemplo de URL:**
```
https://script.google.com/macros/d/1QWxyz9k_AbCdEfGh1ijKl2mN-oPqRsT/usercache
```

---

## PASO 6: Preparar Maqueta HTML para Comisionados

1. Compartí el archivo `sistema_evaluacion_maqueta_v2.html` con los 3 comisionados
   - Pueden abrirlo en navegador (Chrome, Firefox, Safari)
   - No requiere instalación ni servidor
   - Funciona completamente local

2. **Instrucciones para cada comisionado:**
   - Abrir el HTML en navegador
   - Completar identificación (paso 1)
   - Evaluar las 7 áreas (paso 2)
   - Registrar tiempo e incidentes (paso 3)
   - Clic en "Enviar evaluación a la Secretaría Técnica"
   - **Pegar la URL de Google Apps Script** que les compartiste
   - Clic en "Enviar evaluación a Google Sheets"
   - Esperar confirmación verde "✓ Enviado correctamente"

---

## PASO 7: Monitorear Datos

1. En Google Sheets, ir a hoja **"Datos brutos"**
2. Cuando cada comisionado envíe, aparecerá una fila nueva automáticamente
3. Fechas/horas de envío en columna A

**¿Cómo sé que funcionó?**
- Hoja "Datos brutos": 3 filas (una por comisionado) con todos los datos
- Hoja "Consolidación": Se llena automáticamente con fórmulas (lado a lado)
- Hoja "Deliberación": Espera a que ustedes la completen manualmente

---

## PASO 8: Deliberación

Una vez que los 3 hayan enviado:

1. Ir a hoja **"Consolidación"**
   - Ven las 3 evaluaciones lado a lado
   - Ven divergencias destacadas (naranja si hay discrepancia)

2. Ir a hoja **"Deliberación"**
   - **Por cada área** (Docencia, I+D, etc.):
     - Lean los 3 niveles + fundamentos (vienen de Consolidación)
     - Anoten en "Notas de la comisión" qué decidieron y por qué
     - Seleccionen el "Nivel acordado" (0-4)
     - Anoten quién firma esa decisión
   - Repitan para las 7 áreas

3. Ir a hoja **"Resultado Final"**
   - Se completa automáticamente con los niveles acordados
   - Calificación final (Art. 35) se calcula sola
   - Pueden agregar observaciones generales

---

## PASO 9: Exportar Resultado

1. En hoja "Resultado Final", menú ≡ (arriba a izq) → **Descargar** → **PDF (Documento actual)**
2. Se descarga PDF con todo el resultado
3. Pueden compartir o imprimir para archivo

---

## Troubleshooting

### Error: "No se puede acceder a la URL"
**Causa:** URL del Apps Script no es pública o está mal copiada.
**Solución:**
1. Verificá que la URL comienza con `https://script.google.com/macros/d/`
2. En Apps Script, revisá que el deployment existe (Implementar → Implementaciones)
3. Verificá permisos: "Quién tiene acceso" debe ser "Cualquiera que tenga el enlace"

### Error: "Datos incompletos"
**Causa:** La maqueta no está mandando todos los campos.
**Solución:**
1. Verificá que evaluaste todas las 7 áreas
2. Completaste paso 1 (identificación completa)
3. Confirmaste los 2 checks de comprensión (paso 2)

### Datos no aparecen en Sheets
**Causa:** Apps Script no está activado o hay error en ejecución.
**Solución:**
1. En Apps Script, ir a "Ejecuciones" (panel izquierdo)
2. Ver si hay errores en ejecuciones previas
3. Reejecutar `inicializarHojas()` si es necesario

### Las fórmulas de Consolidación no se actualizan
**Causa:** Sheets no refresca automáticamente.
**Solución:**
1. F5 para refrescar la página
2. O, en Apps Script, ejecutar manualmente `actualizarConsolidacion()` desde el menú de funciones

---

## Archivos Necesarios

Asegúrate de tener:

1. ✅ `sistema_evaluacion_maqueta_v2.html` — maqueta (compartir con comisionados)
2. ✅ `apps_script_deliberacion.gs` — código a copiar en Google Sheets
3. ✅ `sistema_deliberacion_estructura.md` — este documento
4. ✅ `IMPLEMENTACION_GOOGLE_SHEETS.md` — este paso a paso

---

## Notas Importantes

- **Confidencialidad (Art. 52):** El Google Sheet es privado (solo comparten link). No compartir públicamente.
- **Integridad de datos:** Apps Script registra timestamp de cada envío (auditoría).
- **Tiempo límite:** No hay. Pueden deliberar el tiempo que necesiten.
- **Cambios post-envío:** Si un comisionado quiere cambiar su evaluación, puede reenviarse (última versión reemplaza anterior en Sheets).
- **Deliberación abierta:** Todas las decisiones quedan registradas en "Deliberación" (trazabilidad Art. 35, Título IX).

---

## Contacto Técnico

Si hay problemas:
1. Revisar el "Troubleshooting" arriba
2. Ejecutar `inicializarHojas()` nuevamente desde Apps Script
3. Compartir pantallazo del error con Secretaría Técnica
