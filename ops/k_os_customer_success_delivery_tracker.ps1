param(
    [ValidateSet("Init", "CreateDemo", "CreateAccount", "AddTask", "SetTaskStatus", "SetHealth", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$CustomerAlias = "",

    [string]$Owner = "k_os_operator",

    [string]$AccountId = "",

    [string]$TaskId = "",

    [string]$Title = "",

    [string]$Priority = "medium",

    [string]$DueDate = "",

    [string]$Status = "",

    [string]$Reason = "",

    [string]$Health = "yellow",

    [string]$RiskLevel = "medium",

    [string]$NextAction = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = "python"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

switch ($Action) {
    "Init" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode create-demo
    }
    "CreateAccount" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode create-account --customer-alias $CustomerAlias --owner $Owner
    }
    "AddTask" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode add-task --account-id $AccountId --title $Title --priority $Priority --owner $Owner --due-date $DueDate
    }
    "SetTaskStatus" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode set-task-status --task-id $TaskId --status $Status --reason $Reason
    }
    "SetHealth" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode set-health --account-id $AccountId --health $Health --risk-level $RiskLevel --next-action $NextAction
    }
    "Audit" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_customer_success_delivery_tracker.py" --mode show
    }
}