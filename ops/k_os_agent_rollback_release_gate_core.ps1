param(
    [ValidateSet("Init", "Decide", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Decision = "block_future_rollback",

    [string]$Operator = "operator_k_os",

    [string]$Reason = ""
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
        & $Python "ops\k_os_agent_rollback_release_gate_core.py" --mode init
    }
    "Decide" {
        & $Python "ops\k_os_agent_rollback_release_gate_core.py" --mode decide --decision $Decision --operator $Operator --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_rollback_release_gate_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_rollback_release_gate_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_rollback_release_gate_core.py" --mode show
    }
}