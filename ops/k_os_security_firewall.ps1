param(
    [ValidateSet("ScanStaged", "ScanWorking", "InstallHook", "SmokeTest")]
    [string]$Action = "ScanWorking"
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
    "ScanStaged" {
        & $Python "ops\k_os_security_firewall.py" --mode scan-staged
    }
    "ScanWorking" {
        & $Python "ops\k_os_security_firewall.py" --mode scan-working
    }
    "InstallHook" {
        & $Python "ops\k_os_security_firewall.py" --mode install-hook
    }
    "SmokeTest" {
        & $Python "ops\k_os_security_firewall.py" --mode smoke-test
    }
}