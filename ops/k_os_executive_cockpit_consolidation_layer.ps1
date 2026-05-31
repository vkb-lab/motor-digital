param(
    [ValidateSet("Init", "Audit", "Navigation", "Health", "Show")]
    [string]$Action = "Audit"
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
    "Init" {
        & $Python "ops\k_os_executive_cockpit_consolidation_layer.py" --mode init
    }
    "Audit" {
        & $Python "ops\k_os_executive_cockpit_consolidation_layer.py" --mode audit
    }
    "Navigation" {
        & $Python "ops\k_os_executive_cockpit_consolidation_layer.py" --mode navigation
    }
    "Health" {
        & $Python "ops\k_os_executive_cockpit_consolidation_layer.py" --mode health
    }
    "Show" {
        & $Python "ops\k_os_executive_cockpit_consolidation_layer.py" --mode show
    }
}