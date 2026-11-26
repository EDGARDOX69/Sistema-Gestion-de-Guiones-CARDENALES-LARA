# Envoltorio local de scripts/ci_tareas.py para Windows/PowerShell.
# Uso: .\scripts\ci_tareas.ps1 -Etapas unidad integracion
param(
    [string[]]$Etapas = @()
)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

$python = if (Test-Path (Join-Path $raiz 'venv\Scripts\python.exe')) {
    Join-Path $raiz 'venv\Scripts\python.exe'
} else {
    'python'
}

$argumentos = @((Join-Path $raiz 'scripts\ci_tareas.py'))
if ($Etapas.Count -gt 0) { $argumentos += @('--etapas') + $Etapas }

& $python @argumentos
exit $LASTEXITCODE
