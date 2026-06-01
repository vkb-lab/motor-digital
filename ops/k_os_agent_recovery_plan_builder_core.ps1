param(
    [ValidateSet("Init", "Build", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Operator = "operator_k_os",

    [string]$Reason = "",

    [string]$Scope = "controlled_recovery_scope"
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
        & $Python "ops\k_os_agent_recovery_plan_builder_core.py" --mode init
    }
    "Build" {
        & $Python "ops\k_os_agent_recovery_plan_builder_core.py" --mode build --operator $Operator --reason $Reason --scope $Scope
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_recovery_plan_builder_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_recovery_plan_builder_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_recovery_plan_builder_core.py" --mode show
    }
}