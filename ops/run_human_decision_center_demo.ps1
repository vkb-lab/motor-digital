param(
    [int]$Stage = 63
)

$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$PythonExe = $null
$PythonArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonExe = "py"
    $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonExe = "python"
} else {
    throw "Python nao encontrado no PATH."
}

Write-Host "Running K-Atlas Human Decision Center smoke test..."
& $PythonExe @PythonArgs ".\agents\human_decision_center.py" --smoke-test --stage $Stage

if ($LASTEXITCODE -ne 0) {
    throw "Human Decision Center smoke test failed."
}

Write-Host "Human Decision Center smoke test finished."
