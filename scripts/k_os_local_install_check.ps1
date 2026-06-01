$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:GIT_PAGER = "cat"

$Root = Split-Path -Parent $PSScriptRoot
cd $Root

Write-Host "K-OS LOCAL INSTALL CHECK"
Write-Host "Modo: checagem somente leitura. Nenhuma dependencia sera instalada."

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

Write-Host "Python detectado:"
& $PythonExe @PythonPrefix --version

if (Test-Path "requirements.txt") {
    Write-Host "requirements.txt encontrado."
} else {
    Write-Host "requirements.txt nao encontrado."
}

$Entrypoint = @("app.py", "streamlit_app.py", "Home.py") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($Entrypoint) {
    Write-Host "Entrypoint Streamlit encontrado: $Entrypoint"
} else {
    Write-Host "Nenhum entrypoint Streamlit encontrado."
}

$StreamlitCheck = & $PythonExe @PythonPrefix -c "import importlib.util; print('streamlit_available=' + str(importlib.util.find_spec('streamlit') is not None).lower())"
Write-Host $StreamlitCheck

Write-Host "Checagem local finalizada."