param(
    [ValidateSet("Init", "RegisterAgent", "Heartbeat", "Watchdog", "CreateDemo", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$AgentId = "k_atlas_engineer",

    [string]$TaskId = "",

    [string]$ActionId = "",

    [string]$RuntimeStatus = "active",

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
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode init
    }
    "RegisterAgent" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode register-agent --agent-id $AgentId --reason $Reason
    }
    "Heartbeat" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode heartbeat --agent-id $AgentId --task-id $TaskId --action-id $ActionId --status $RuntimeStatus --reason $Reason
    }
    "Watchdog" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode watchdog
    }
    "CreateDemo" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode create-demo
    }
    "Audit" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_runtime_supervisor_core.py" --mode show
    }
}