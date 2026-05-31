param(
    [ValidateSet("Init", "CreateDemo", "Audit", "AddCustomer", "SetStatus", "LinkRecord", "Show")]
    [string]$Action = "Audit",

    [string]$Alias = "",

    [string]$Source = "manual",

    [string]$Owner = "k_os_operator",

    [string]$NextAction = "qualificar lead",

    [string]$AgentId = "",

    [string]$CustomerId = "",

    [string]$Status = "",

    [string]$Reason = "",

    [string]$LinkType = "",

    [string]$Target = ""
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
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode create-demo
    }
    "Audit" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode audit
    }
    "AddCustomer" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode add-customer --alias $Alias --source $Source --owner $Owner --next-action $NextAction --agent-id $AgentId
    }
    "SetStatus" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode set-status --customer-id $CustomerId --status $Status --reason $Reason
    }
    "LinkRecord" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode link-record --customer-id $CustomerId --link-type $LinkType --target $Target
    }
    "Show" {
        & $Python "ops\k_os_customer_registry_crm_core.py" --mode show
    }
}