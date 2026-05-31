param(
    [ValidateSet("Init", "Audit", "Dashboard", "Health", "Show")]
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
        & $Python "ops\k_os_analytics_executive_metrics_core.py" --mode init
    }
    "Audit" {
        & $Python "ops\k_os_analytics_executive_metrics_core.py" --mode audit
    }
    "Dashboard" {
        & $Python "ops\k_os_analytics_executive_metrics_core.py" --mode dashboard
    }
    "Health" {
        & $Python "ops\k_os_analytics_executive_metrics_core.py" --mode health
    }
    "Show" {
        & $Python "ops\k_os_analytics_executive_metrics_core.py" --mode show
    }
}