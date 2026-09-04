# Funciones compartidas por los scripts de automatización de Inkscape.

function Get-InkscapePath {
    <#
        .SYNOPSIS
        Resuelve la ruta al ejecutable inkscape.exe, en este orden de prioridad:
        1) config/inkscape.config.json
        2) inkscape disponible en el PATH del sistema
        3) ruta de instalación por defecto en Windows
    #>
    param(
        [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\config\inkscape.config.json")
    )

    if (Test-Path $ConfigPath) {
        try {
            $config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
            if ($config.inkscapePath -and (Test-Path $config.inkscapePath)) {
                return $config.inkscapePath
            }
        } catch {
            Write-Warning "No se pudo leer $ConfigPath, se buscará Inkscape por otros medios."
        }
    }

    $cmd = Get-Command inkscape -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $rutasComunes = @(
        "C:\Program Files\Inkscape\bin\inkscape.exe",
        "C:\Program Files (x86)\Inkscape\bin\inkscape.exe"
    )
    foreach ($ruta in $rutasComunes) {
        if (Test-Path $ruta) { return $ruta }
    }

    throw "No se encontró inkscape.exe. Instala Inkscape, agrégalo al PATH, o configura la ruta correcta en config/inkscape.config.json."
}
