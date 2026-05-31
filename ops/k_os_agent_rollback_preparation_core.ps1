param(
    [ValidateSet("Init", "Prepare", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Scope = "agent_execution_chain",

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
        & $Python "ops\k_os_agent_rollback_preparation_core.py" --mode init
    }
    "Prepare" {
        & $Python "ops\k_os_agent_rollback_preparation_core.py" --mode prepare --scope $Scope --reason $Reason --operator $Operator
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_rollback_preparation_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_rollback_preparation_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_rollback_preparation_core.py" --mode show
    }
}