param(
    [ValidateSet("Init", "CreateDemo", "Audit", "AddDeal", "UpdateStage", "ApprovalDryRun", "Show")]
    [string]$Action = "Audit",

    [string]$CustomerAlias = "",

    [string]$AgentId = "marketplace_ia_agent",

    [double]$MRR = 0,

    [double]$Setup = 0,

    [string]$Priority = "medium",

    [string]$Owner = "k_os_operator",

    [string]$NextAction = "qualificar oportunidade",

    [string]$DealId = "",

    [string]$Stage = "",

    [string]$Reason = "",

    [int]$Probability = -1
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
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode create-demo
    }
    "Audit" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode audit
    }
    "AddDeal" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode add-deal --customer-alias $CustomerAlias --agent-id $AgentId --mrr $MRR --setup $Setup --priority $Priority --owner $Owner --next-action $NextAction
    }
    "UpdateStage" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode update-stage --deal-id $DealId --stage $Stage --reason $Reason --probability $Probability
    }
    "ApprovalDryRun" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode approval-dry-run --deal-id $DealId
    }
    "Show" {
        & $Python "ops\k_os_sales_pipeline_deal_desk.py" --mode show
    }
}