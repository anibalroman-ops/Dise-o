<#
    .SYNOPSIS
    Exporta un archivo SVG de Inkscape a PDF, PNG u otro formato desde la línea de comandos.

    .EXAMPLE
    .\Export-Diagram.ps1 -InputSvg .\templates\informe_basico.svg -Format pdf

    .EXAMPLE
    .\Export-Diagram.ps1 -InputSvg .\output\generados\informe_ejemplo.svg -Format png -Dpi 300
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InputSvg,
    [Parameter(Mandatory)][ValidateSet('pdf', 'png', 'svg', 'eps', 'ps')]
    [string]$Format,
    [string]$OutputPath,
    [int]$Dpi = 300,
    [switch]$AreaDrawing
)

. (Join-Path $PSScriptRoot "Common.ps1")

if (-not (Test-Path $InputSvg)) {
    throw "No existe el archivo: $InputSvg"
}

if (-not $OutputPath) {
    $OutputPath = [System.IO.Path]::ChangeExtension($InputSvg, $Format)
}

$inkscape = Get-InkscapePath

$argsList = @(
    (Resolve-Path $InputSvg).Path,
    "--export-type=$Format",
    "--export-filename=$OutputPath",
    "--export-dpi=$Dpi"
)
if ($AreaDrawing) { $argsList += "--export-area-drawing" }

$destDir = Split-Path $OutputPath
if ($destDir) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }

Write-Host "Exportando '$InputSvg' -> '$OutputPath' ($Format, $Dpi dpi)..."
& $inkscape @argsList
if ($LASTEXITCODE -ne 0) {
    throw "Inkscape terminó con código de salida $LASTEXITCODE"
}
Write-Host "Listo: $OutputPath"
