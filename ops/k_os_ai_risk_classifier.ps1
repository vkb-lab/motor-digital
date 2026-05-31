param(
    [ValidateSet("SmokeTest", "ScanPolicy", "Classify")]
    [string]$Action = "SmokeTest",

    [string]$Text = "",

    [string]$Agent = "",

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
    "SmokeTest" {
        & $Python "ops\k_os_ai_risk_classifier.py" --mode smoke-test
    }
    "ScanPolicy" {
        & $Python "ops\k_os_ai_risk_classifier.py" --mode scan-policy
    }
    "Classify" {
        & $Python "ops\k_os_ai_risk_classifier.py" --mode classify --action $Text --agent $Agent --target $Target
    }
}