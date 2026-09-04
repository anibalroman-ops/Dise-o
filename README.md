# Automatización de diagramas con Inkscape + VS Code (Windows)

Herramientas para generar y exportar en lote los diagramas de tus informes/reportes
de investigación diseñados en Inkscape, controlado desde la línea de comandos de
Windows (PowerShell) e integrado como tareas de Visual Studio Code.

## Requisitos

- [Inkscape 1.x](https://inkscape.org/release) instalado en Windows.
- PowerShell 5.1 (viene con Windows) o PowerShell 7+.
- Visual Studio Code.

Recomendado: agregar Inkscape al `PATH` del sistema durante la instalación. Si no lo
hiciste, edita `config/inkscape.config.json` con la ruta real de `inkscape.exe`.

## Estructura del repositorio

```
config/                    Configuración (ruta a Inkscape)
templates/                 Plantillas .svg diseñadas en Inkscape (con ids en los objetos)
data/                      Archivos JSON con los datos de cada informe
scripts/ps/                Scripts de PowerShell que hablan con Inkscape
docs/                      Referencia de comandos y acciones de Inkscape
output/generados/          SVG generados a partir de una plantilla + datos
output/pdf/, output/png/   Exportaciones finales
.vscode/tasks.json         Tareas de VS Code para ejecutar todo con un clic
```

## Flujo de trabajo recomendado

1. **Diseña la plantilla en Inkscape** como siempre (títulos, gráficos, textos).
   A cada elemento que quieras rellenar automáticamente (título, fecha, valores,
   etiquetas) asígnale un **id** descriptivo desde *Objeto > Propiedades del
   objeto* (`Ctrl+Shift+O`), por ejemplo `titulo`, `valor1`, `etiqueta1`.
   Guarda la plantilla en `templates/` (ver `templates/informe_basico.svg` de ejemplo).

2. **Define los datos del informe** en un JSON dentro de `data/`, con una clave por
   cada id de la plantilla (ver `data/ejemplo_informe.json`).

3. **Genera el diagrama** combinando plantilla + datos:

   ```powershell
   .\scripts\ps\New-FromTemplate.ps1 `
       -TemplatePath .\templates\informe_basico.svg `
       -DataFile .\data\ejemplo_informe.json `
       -OutputSvg .\output\generados\informe_ejemplo.svg `
       -ExportarPdf
   ```

   Esto crea el SVG final en `output/generados/` y, con `-ExportarPdf` (o
   `-ExportarPng`), además genera el PDF/PNG listo para el informe.

4. **Exporta en lote** todos los diagramas generados de una vez:

   ```powershell
   .\scripts\ps\Export-AllDiagrams.ps1 -Format pdf
   ```

5. Para instrucciones puntuales sobre un diagrama (mover, alinear, cambiar color de
   un elemento por su id, etc.) usa las *acciones* de Inkscape vía:

   ```powershell
   .\scripts\ps\Invoke-InkscapeAction.ps1 -InputSvg .\templates\informe_basico.svg `
       -Actions "select-by-id:barra1;object-set-attribute:fill,#2e7d32;select-clear"
   ```

   La lista de acciones disponibles y más ejemplos están en
   `docs/inkscape-cli-referencia.md`.

## Usar los scripts desde Visual Studio Code

El repo incluye `.vscode/tasks.json` con tareas listas para usar. Desde VS Code:

- `Ctrl+Shift+P` → **Tasks: Run Task** → elige, por ejemplo,
  **"Inkscape: Exportar SVG activo a PDF"** (exporta el archivo que tienes abierto).
- `Ctrl+Shift+B` ejecuta la tarea por defecto: genera el informe de ejemplo completo
  (plantilla + datos → SVG → PDF).
- También puedes abrir la terminal integrada de VS Code (`` Ctrl+ñ `` o
  *Terminal > New Terminal*) y ejecutar cualquiera de los scripts directamente en
  PowerShell.

Puedes asignar atajos de teclado propios a estas tareas desde
*File > Preferences > Keyboard Shortcuts* buscando `workbench.action.tasks.runTask`
y apuntando al `label` de la tarea deseada.

## Scripts disponibles

| Script | Uso |
|---|---|
| `scripts/ps/Export-Diagram.ps1` | Exporta un único SVG a PDF/PNG/etc. |
| `scripts/ps/Export-AllDiagrams.ps1` | Exporta en lote todos los SVG de una carpeta |
| `scripts/ps/New-FromTemplate.ps1` | Rellena una plantilla con datos de un JSON y opcionalmente exporta |
| `scripts/ps/Invoke-InkscapeAction.ps1` | Ejecuta acciones arbitrarias de Inkscape (alinear, mover, cambiar color, etc.) |
| `scripts/ps/Common.ps1` | Función compartida para localizar `inkscape.exe` |

Cada script tiene ayuda incorporada: `Get-Help .\scripts\ps\Export-Diagram.ps1 -Full`.

## Extender

- Agrega más plantillas en `templates/` reutilizando el mismo patrón de ids.
- Crea un `data/*.json` por cada informe/investigación.
- Si necesitas lógica más compleja (por ejemplo, generar decenas de informes desde
  una tabla de datos, o dibujar gráficos dinámicamente en vez de solo rellenar
  texto), estos mismos scripts de PowerShell pueden invocarse en bucle desde otro
  script, o migrarse a Python (`lxml`/`inkex`) manteniendo el mismo enfoque de
  "plantilla con ids + datos externos".
