<#
    .SYNOPSIS
    Genera un diagrama SVG a partir de una plantilla, reemplazando los textos marcados
    con un "id" (título, fecha, valores, etiquetas, etc.) según un archivo de datos JSON.

    .DESCRIPTION
    En Inkscape, a cualquier objeto (texto, rectángulo, grupo) se le puede asignar un
    identificador desde Editar > Propiedades del objeto ("Id"). Este script busca esos
    identificadores en el SVG y reemplaza su contenido de texto con los valores del
    archivo JSON indicado, generando así un nuevo diagrama sin abrir Inkscape.

    .EXAMPLE
    .\New-FromTemplate.ps1 `
        -TemplatePath .\templates\informe_basico.svg `
        -DataFile .\data\ejemplo_informe.json `
        -OutputSvg .\output\generados\informe_ejemplo.svg `
        -ExportarPdf
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$TemplatePath,
    [Parameter(Mandatory)][string]$DataFile,
    [Parameter(Mandatory)][string]$OutputSvg,
    [switch]$ExportarPdf,
    [switch]$ExportarPng,
    [int]$Dpi = 300
)

if (-not (Test-Path $TemplatePath)) { throw "No existe la plantilla: $TemplatePath" }
if (-not (Test-Path $DataFile)) { throw "No existe el archivo de datos: $DataFile" }

$datos = Get-Content -Path $DataFile -Raw | ConvertFrom-Json

[xml]$doc = Get-Content -Path $TemplatePath -Raw
$ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
$ns.AddNamespace('svg', 'http://www.w3.org/2000/svg')

foreach ($prop in $datos.PSObject.Properties) {
    $id = $prop.Name
    $texto = [string]$prop.Value

    $nodo = $doc.SelectSingleNode("//svg:*[@id='$id']", $ns)
    if (-not $nodo) {
        Write-Warning "No se encontró ningún elemento con id='$id' en la plantilla; se omite."
        continue
    }

    # El texto de un <text> en Inkscape normalmente vive dentro de un <tspan> hijo.
    $tspan = $nodo.SelectSingleNode(".//svg:tspan", $ns)
    if ($tspan) {
        $tspan.InnerText = $texto
    } else {
        $nodo.InnerText = $texto
    }
}

$destDir = Split-Path $OutputSvg
if ($destDir) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
$doc.Save($OutputSvg)
Write-Host "Diagrama generado: $OutputSvg"

if ($ExportarPdf) {
    & (Join-Path $PSScriptRoot "Export-Diagram.ps1") -InputSvg $OutputSvg -Format pdf -Dpi $Dpi
}
if ($ExportarPng) {
    & (Join-Path $PSScriptRoot "Export-Diagram.ps1") -InputSvg $OutputSvg -Format png -Dpi $Dpi
}
