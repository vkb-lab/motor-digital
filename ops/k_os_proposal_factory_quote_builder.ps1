param(
    [ValidateSet("Init", "CreateDemo", "CreateFromDeal", "Audit", "SetStatus", "ApprovalDryRun", "Show")]
    [string]$Action = "Audit",

    [string]$DealId = "",

    [string]$ProposalId = "",

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
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode create-demo
    }
    "CreateFromDeal" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode create-from-deal --deal-id $DealId
    }
    "Audit" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode audit
    }
    "SetStatus" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode set-status --proposal-id $ProposalId --status $Status --reason $Reason
    }
    "ApprovalDryRun" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode approval-dry-run --proposal-id $ProposalId
    }
    "Show" {
        & $Python "ops\k_os_proposal_factory_quote_builder.py" --mode show
    }
}