param(
    [ValidateSet("Init", "CreateDemo", "CreateTask", "ApproveTask", "DispatchTask", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$AgentId = "k_atlas_engineer",

    [string]$ActionId = "",

    [string]$Title = "",

    [string]$Priority = "medium",

    [string]$Reason = "",

    [string]$TaskId = "",

    [switch]$Approved,

    [switch]$Execute
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
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode create-demo
    }
    "CreateTask" {
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode create-task --agent-id $AgentId --action-id $ActionId --title $Title --priority $Priority --reason $Reason
    }
    "ApproveTask" {
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode approve-task --task-id $TaskId --reason $Reason
    }
    "DispatchTask" {
        $ArgsList = @("ops\k_os_agent_orchestration_queue_core.py", "--mode", "dispatch-task", "--task-id", $TaskId)

        if ($Approved) {
            $ArgsList += "--approved"
        }

        if ($Execute) {
            $ArgsList += "--execute"
        }

        if ($Reason -ne "") {
            $ArgsList += @("--reason", $Reason)
        }

        & $Python @ArgsList
    }
    "Audit" {
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_orchestration_queue_core.py" --mode show
    }
}