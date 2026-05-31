param(
    [ValidateSet("SmokeTest", "ScanLocal", "ValidateFile")]
    [string]$Action = "ScanLocal",

    [string]$Path = "",

    [string]$Schema = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

switch ($Action) {
    "SmokeTest" {
        & $Python "ops\k_os_schema_guard.py" --mode smoke-test
    }
    "ScanLocal" {
        & $Python "ops\k_os_schema_guard.py" --mode scan-local
    }
    "ValidateFile" {
        if ([string]::IsNullOrWhiteSpace($Path)) {
            throw "Informe -Path para ValidateFile."
        }

        if ([string]::IsNullOrWhiteSpace($Schema)) {
            & $Python "ops\k_os_schema_guard.py" --mode validate-file --path $Path
        } else {
            & $Python "ops\k_os_schema_guard.py" --mode validate-file --path $Path --schema $Schema
        }
    }
}