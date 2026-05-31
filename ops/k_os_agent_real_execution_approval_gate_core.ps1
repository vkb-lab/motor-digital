param(
    [ValidateSet("Init", "Approve", "Block", "Revoke", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

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
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode init
    }
    "Approve" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode approve --operator $Operator --reason $Reason
    }
    "Block" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode block --operator $Operator --reason $Reason
    }
    "Revoke" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode revoke --operator $Operator --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_real_execution_approval_gate_core.py" --mode show
    }
}