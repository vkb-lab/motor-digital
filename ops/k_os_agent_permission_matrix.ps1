param(
    [ValidateSet("Validate", "Show")]
    [string]$Action = "Validate"
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
    "Validate" {
        & $Python "ops\k_os_agent_permission_matrix.py" --mode validate
    }
    "Show" {
        & $Python "ops\k_os_agent_permission_matrix.py" --mode show
    }
}