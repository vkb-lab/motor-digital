param(
    [ValidateSet("Init", "Sandbox", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$SandboxMode = "safe_block",

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
        & $Python "ops\k_os_agent_rollback_controlled_sandbox_core.py" --mode init
    }
    "Sandbox" {
        & $Python "ops\k_os_agent_rollback_controlled_sandbox_core.py" --mode sandbox --sandbox-mode $SandboxMode --operator $Operator --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_rollback_controlled_sandbox_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_rollback_controlled_sandbox_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_rollback_controlled_sandbox_core.py" --mode show
    }
}