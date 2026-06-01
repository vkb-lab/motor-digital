param(
    [ValidateSet("Init", "Review", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$ReviewMode = "acknowledge_blocked",

    [string]$Operator = "operator_k_os",

    [string]$Notes = ""
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
        & $Python "ops\k_os_agent_recovery_sandbox_review_core.py" --mode init
    }
    "Review" {
        & $Python "ops\k_os_agent_recovery_sandbox_review_core.py" --mode review --review-mode $ReviewMode --operator $Operator --notes $Notes
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_recovery_sandbox_review_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_recovery_sandbox_review_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_recovery_sandbox_review_core.py" --mode show
    }
}