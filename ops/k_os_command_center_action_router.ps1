param(
    [ValidateSet("Init", "Audit", "Catalog", "Route", "Show")]
    [string]$Action = "Audit",

    [string]$ActionId = "",

    [switch]$Approved,

    [string]$Reason = "",

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
        & $Python "ops\k_os_command_center_action_router.py" --mode init
    }
    "Audit" {
        & $Python "ops\k_os_command_center_action_router.py" --mode audit
    }
    "Catalog" {
        & $Python "ops\k_os_command_center_action_router.py" --mode catalog
    }
    "Route" {
        $ArgsList = @("ops\k_os_command_center_action_router.py", "--mode", "route", "--action-id", $ActionId)

        if ($Approved) {
            $ArgsList += "--approved"
        }

        if ($Reason -ne "") {
            $ArgsList += @("--reason", $Reason)
        }

        if ($Execute) {
            $ArgsList += "--execute"
        }

        & $Python @ArgsList
    }
    "Show" {
        & $Python "ops\k_os_command_center_action_router.py" --mode show
    }
}