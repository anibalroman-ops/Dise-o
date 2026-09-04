# Referencia rápida: Inkscape por línea de comandos (Windows)

Inkscape 1.x trae dos mecanismos para automatización desde la consola:

1. **Opciones de exportación** (`--export-*`): para convertir SVG a PDF/PNG/etc.
2. **Acciones** (`--actions`): una API de comandos encadenables que reproducen lo
   que harías con el mouse/teclado dentro de Inkscape (seleccionar, alinear, mover,
   escalar, cambiar atributos, exportar...).

Para ver la lista completa de acciones disponibles en tu versión instalada:

```powershell
inkscape --action-list
```

## Exportar un archivo

```powershell
# PDF
inkscape "C:\ruta\diagrama.svg" --export-type=pdf --export-filename="C:\ruta\diagrama.pdf"

# PNG a 300 dpi
inkscape "C:\ruta\diagrama.svg" --export-type=png --export-dpi=300 --export-filename="C:\ruta\diagrama.png"

# Solo el área con contenido (recorta márgenes vacíos de la página)
inkscape "C:\ruta\diagrama.svg" --export-type=pdf --export-area-drawing --export-filename="C:\ruta\diagrama.pdf"
```

Equivalente con los scripts de este repo:

```powershell
.\scripts\ps\Export-Diagram.ps1 -InputSvg .\templates\informe_basico.svg -Format pdf
```

## Acciones útiles para automatizar diagramas

Las acciones se combinan separadas por `;` en un solo `--actions="..."`.

| Acción | Qué hace |
|---|---|
| `select-by-id:MI_ID` | Selecciona el objeto con ese id (asignado en Inkscape vía Editar > Propiedades del objeto) |
| `select-all` | Selecciona todos los objetos de la página/capa actual |
| `select-clear` | Deselecciona todo |
| `object-set-attribute:atributo,valor` | Cambia un atributo XML del objeto seleccionado (ej. `fill,#2e7d32`) |
| `transform-move:dx,dy` | Mueve la selección |
| `transform-scale:factor` | Escala la selección |
| `object-align-horizontal-center` / `align-horizontal-center-page` | Alinea objetos |
| `export-filename:ruta` | Define el archivo de salida para la siguiente exportación |
| `export-type:pdf` \| `png` | Define el formato de exportación |
| `export-dpi:300` | Resolución para PNG |
| `export-do` | Ejecuta la exportación con lo configurado antes |
| `file-save` | Guarda el archivo actual (sobrescribe) |
| `quit` | Cierra Inkscape |

### Ejemplo: cambiar el color de una barra y exportar

```powershell
inkscape "informe.svg" --actions="select-by-id:barra1;object-set-attribute:fill,#c62828;select-clear;export-type:pdf;export-filename:informe.pdf;export-do"
```

Equivalente con el script del repo:

```powershell
.\scripts\ps\Invoke-InkscapeAction.ps1 -InputSvg .\templates\informe_basico.svg `
    -Actions "select-by-id:barra1;object-set-attribute:fill,#c62828;select-clear"
```

## Modo shell (procesar varios comandos sin reabrir Inkscape cada vez)

```powershell
inkscape --shell
```

Dentro del modo interactivo puedes escribir acciones línea por línea, útil para
probar antes de meterlas en un script. Se sale con `quit`.

## Notas

- Los IDs se asignan en Inkscape desde el panel **Objeto > Propiedades del objeto**
  (o `Ctrl+Shift+O`). Usa IDs descriptivos y estables (`titulo`, `barra1`, `valor1`)
  para que los scripts de este repo puedan encontrarlos de forma confiable.
- Si Inkscape no está en el `PATH`, todos los scripts de `scripts/ps/` leen la ruta
  desde `config/inkscape.config.json`.
