param(
    [ValidateSet("Init", "CreateDemo", "Validate", "CreateCase", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$CustomerAlias = ""
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
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode create-demo
    }
    "Validate" {
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode validate --customer-alias $CustomerAlias
    }
    "CreateCase" {
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode create-case --customer-alias $CustomerAlias
    }
    "Audit" {
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_onboarding_activation_gate.py" --mode show
    }
}