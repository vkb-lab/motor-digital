$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:GIT_PAGER = "cat"

$Root = Split-Path -Parent $PSScriptRoot
cd $Root

$PythonExe = "python"
$PythonPrefix = @()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $PythonPrefix = @("-3")
    } else {
        throw "Python nao encontrado no PATH."
    }
}

& $PythonExe @PythonPrefix "k_atlas\ops\resilience_layer_closure_078.py" init
& $PythonExe @PythonPrefix "k_atlas\ops\resilience_layer_closure_078.py" action
& $PythonExe @PythonPrefix "k_atlas\ops\resilience_layer_closure_078.py" validate
& $PythonExe @PythonPrefix "k_atlas\ops\resilience_layer_closure_078.py" audit
& $PythonExe @PythonPrefix "k_atlas\ops\resilience_layer_closure_078.py" closure

Write-Host "Checkpoint 078 executado com sucesso."