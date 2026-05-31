param(
    [ValidateSet("Init", "CreateDemo", "Audit", "ReconcileDryRun", "SetStatus", "Show")]
    [string]$Action = "Audit",

    [string]$SubscriptionId = "",

    [string]$Status = "",

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
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode create-demo
    }
    "Audit" {
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode audit
    }
    "ReconcileDryRun" {
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode reconcile-dry-run
    }
    "SetStatus" {
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode set-status --subscription-id $SubscriptionId --status $Status --reason $Reason
    }
    "Show" {
        & $Python "ops\k_os_billing_subscription_ledger.py" --mode show
    }
}