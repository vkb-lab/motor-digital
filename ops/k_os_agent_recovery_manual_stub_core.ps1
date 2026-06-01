param(
    [ValidateSet("Init", "Stub", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$StubMode = "record_blocked_intent",

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
        & $Python "ops\k_os_agent_recovery_manual_stub_core.py" --mode init
    }
    "Stub" {
        & $Python "ops\k_os_agent_recovery_manual_stub_core.py" --mode stub --stub-mode $StubMode --operator $Operator --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_recovery_manual_stub_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_recovery_manual_stub_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_recovery_manual_stub_core.py" --mode show
    }
}