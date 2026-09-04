<#
    .SYNOPSIS
    Exporta en lote todos los .svg de una carpeta a PDF o PNG.

    .EXAMPLE
    .\Export-AllDiagrams.ps1 -SourceDir .\output\generados -DestDir .\output\pdf -Format pdf

    .EXAMPLE
    .\Export-AllDiagrams.ps1 -Format png -Dpi 300
#>
[CmdletBinding()]
param(
    [string]$SourceDir = (Join-Path $PSScriptRoot "..\..\output\generados"),
    [string]$DestDir,
    [ValidateSet('pdf', 'png')][string]$Format = 'pdf',
    [int]$Dpi = 300
)

. (Join-Path $PSScriptRoot "Common.ps1")

if (-not $DestDir) {
    $DestDir = Join-Path $PSScriptRoot "..\..\output\$Format"
}

if (-not (Test-Path $SourceDir)) {
    throw "No existe la carpeta de origen: $SourceDir"
}

$inkscape = Get-InkscapePath
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

$svgs = Get-ChildItem -Path $SourceDir -Filter *.svg -File
if (-not $svgs) {
    Write-Warning "No se encontraron archivos .svg en $SourceDir"
    return
}

$exitosos = 0
foreach ($svg in $svgs) {
    $out = Join-Path $DestDir ([System.IO.Path]::ChangeExtension($svg.Name, $Format))
    Write-Host "Exportando $($svg.Name) -> $out"
    & $inkscape $svg.FullName "--export-type=$Format" "--export-filename=$out" "--export-dpi=$Dpi"
    if ($LASTEXITCODE -eq 0) {
        $exitosos++
    } else {
        Write-Warning "Fallo al exportar $($svg.Name) (código $LASTEXITCODE)"
    }
}

Write-Host "Exportación por lote finalizada: $exitosos de $($svgs.Count) archivo(s) en $DestDir"
