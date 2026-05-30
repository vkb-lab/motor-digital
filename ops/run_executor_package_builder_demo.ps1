param(
    [int]$Stage = 64
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

Write-Host "Running K-Atlas Executor Package Builder smoke test..."
& $PythonExe @PythonArgs ".\agents\executor_package_builder.py" --smoke-test --stage $Stage

if ($LASTEXITCODE -ne 0) {
    throw "Executor Package Builder smoke test failed."
}

Write-Host "Executor Package Builder smoke test finished."
