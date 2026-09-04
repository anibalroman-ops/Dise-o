<#
    .SYNOPSIS
    Ejecuta una cadena de "acciones" de Inkscape (la API de comandos de Inkscape 1.x)
    sobre un SVG y guarda el resultado. Útil para instrucciones puntuales que van más
    allá de reemplazar texto: alinear objetos, mover, escalar, cambiar color de relleno, etc.

    .DESCRIPTION
    Las acciones se separan con ";" y se documentan en docs/inkscape-cli-referencia.md
    y en la salida de: inkscape --action-list

    .EXAMPLE
    # Selecciona el objeto con id "barra1" y le cambia el color de relleno
    .\Invoke-InkscapeAction.ps1 -InputSvg .\output\generados\informe_ejemplo.svg `
        -Actions "select-by-id:barra1;object-set-attribute:fill,#2e7d32;select-clear"

    .EXAMPLE
    # Centra todos los objetos horizontalmente en la página
    .\Invoke-InkscapeAction.ps1 -InputSvg .\templates\informe_basico.svg `
        -Actions "select-all;align-horizontal-center-page;select-clear"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InputSvg,
    [Parameter(Mandatory)][string]$Actions,
    [string]$OutputSvg
)

. (Join-Path $PSScriptRoot "Common.ps1")

if (-not (Test-Path $InputSvg)) { throw "No existe el archivo: $InputSvg" }
if (-not $OutputSvg) { $OutputSvg = $InputSvg }

$inkscape = Get-InkscapePath
$destDir = Split-Path $OutputSvg
if ($destDir) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }

$accionesCompletas = "$Actions;export-filename:$OutputSvg;export-do"

Write-Host "Ejecutando acciones de Inkscape sobre '$InputSvg'..."
Write-Host "  $Actions"
& $inkscape (Resolve-Path $InputSvg).Path "--actions=$accionesCompletas"
if ($LASTEXITCODE -ne 0) {
    throw "Inkscape terminó con código de salida $LASTEXITCODE"
}
Write-Host "Listo: $OutputSvg"
