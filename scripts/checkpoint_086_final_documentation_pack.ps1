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

& $PythonExe @PythonPrefix "k_atlas\ops\final_documentation_pack_086.py" init
& $PythonExe @PythonPrefix "k_atlas\ops\final_documentation_pack_086.py" action
& $PythonExe @PythonPrefix "k_atlas\ops\final_documentation_pack_086.py" validate
& $PythonExe @PythonPrefix "k_atlas\ops\final_documentation_pack_086.py" audit
& $PythonExe @PythonPrefix "k_atlas\ops\final_documentation_pack_086.py" closure

Write-Host "Checkpoint 086 executado com sucesso."