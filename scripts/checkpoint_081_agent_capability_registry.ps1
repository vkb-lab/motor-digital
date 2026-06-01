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

& $PythonExe @PythonPrefix "k_atlas\ops\agent_capability_registry_081.py" init
& $PythonExe @PythonPrefix "k_atlas\ops\agent_capability_registry_081.py" action
& $PythonExe @PythonPrefix "k_atlas\ops\agent_capability_registry_081.py" validate
& $PythonExe @PythonPrefix "k_atlas\ops\agent_capability_registry_081.py" audit
& $PythonExe @PythonPrefix "k_atlas\ops\agent_capability_registry_081.py" closure

Write-Host "Checkpoint 081 executado com sucesso."