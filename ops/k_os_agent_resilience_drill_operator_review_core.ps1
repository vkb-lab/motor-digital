param(
    [ValidateSet("Init", "Review", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Operator = "operator_k_os",

    [ValidateSet("reviewed", "reviewed_with_followup", "blocked")]
    [string]$Decision = "reviewed_with_followup",

    [string]$Notes = "",

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
        & $Python "ops\k_os_agent_resilience_drill_operator_review_core.py" --mode init
    }
    "Review" {
        & $Python "ops\k_os_agent_resilience_drill_operator_review_core.py" --mode review --operator $Operator --decision $Decision --notes $Notes --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_resilience_drill_operator_review_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_resilience_drill_operator_review_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_resilience_drill_operator_review_core.py" --mode show
    }
}