param(
    [ValidateSet("Init", "CreateDemo", "Assemble", "ValidateLatest", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$AgentId = "k_atlas_engineer",

    [string]$TaskId = "",

    [string]$ActionId = "",

    [string]$Query = "",

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
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode create-demo
    }
    "Assemble" {
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode assemble --agent-id $AgentId --task-id $TaskId --action-id $ActionId --query $Query --reason $Reason
    }
    "ValidateLatest" {
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode validate-latest
    }
    "Audit" {
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_prompt_assembly_execution_plan_core.py" --mode show
    }
}