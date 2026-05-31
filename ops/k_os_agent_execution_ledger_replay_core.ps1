param(
    [ValidateSet("Init", "RecordLatest", "CreateDemo", "Replay", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$LedgerId = "",

    [string]$Reason = "",

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
        & $Python "ops\k_os_agent_execution_ledger_replay_core.py" --mode init
    }
    "RecordLatest" {
        & $Python "ops\k_os_agent_execution_ledger_replay_core.py" --mode record-latest --reason $Reason
    }
    "CreateDemo" {
        & $Python "ops\k_os_agent_execution_ledger_replay_core.py" --mode create-demo
    }
    "Replay" {
        $ArgsList = @("ops\k_os_agent_execution_ledger_replay_core.py", "--mode", "replay", "--ledger-id", $LedgerId)

        if ($Reason -ne "") {
            $ArgsList += @("--reason", $Reason)
        }

        if ($Approved) {
            $ArgsList += "--approved"
        }

        if ($Execute) {
            $ArgsList += "--execute"
        }

        & $Python @ArgsList
    }
    "Audit" {
        & $Python "ops\k_os_agent_execution_ledger_replay_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_agent_execution_ledger_replay_core.py" --mode show
    }
}