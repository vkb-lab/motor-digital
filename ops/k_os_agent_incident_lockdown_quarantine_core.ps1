param(
    [ValidateSet("Init", "Lockdown", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Scope = "agent_execution_chain",

    [string]$Severity = "SEV3",

    [string]$Reason = "",

    [string]$Operator = "operator_k_os"
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
        & $Python "ops\k_os_agent_incident_lockdown_quarantine_core.py" --mode init
    }
    "Lockdown" {
        & $Python "ops\k_os_agent_incident_lockdown_quarantine_core.py" --mode lockdown --scope $Scope --severity $Severity --reason $Reason --operator $Operator
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_incident_lockdown_quarantine_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_incident_lockdown_quarantine_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_incident_lockdown_quarantine_core.py" --mode show
    }
}