param(
    [ValidateSet("Init", "IssueDemo", "Audit", "Lockdown", "Revoke")]
    [string]$Action = "Audit",

    [string]$LicenseId = "",

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
        & $Python "ops\k_os_license_gate.py" --mode init
    }
    "IssueDemo" {
        & $Python "ops\k_os_license_gate.py" --mode issue-demo
    }
    "Audit" {
        & $Python "ops\k_os_license_gate.py" --mode audit
    }
    "Lockdown" {
        & $Python "ops\k_os_license_gate.py" --mode lockdown --reason $Reason
    }
    "Revoke" {
        & $Python "ops\k_os_license_gate.py" --mode revoke --license-id $LicenseId --reason $Reason
    }
}