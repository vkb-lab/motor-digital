param(
    [ValidateSet("Generate", "Show")]
    [string]$Action = "Generate"
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
    "Generate" {
        & $Python "ops\k_os_mission_control_2.py" --mode generate
    }
    "Show" {
        & $Python "ops\k_os_mission_control_2.py" --mode show
    }
}