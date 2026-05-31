param(
    [ValidateSet("SmokeTest", "Simulate", "ShowPolicy")]
    [string]$Action = "SmokeTest",

    [string]$Provider = "openai",

    [string]$UseCase = "text_brief",

    [string]$Prompt = "Sandbox prompt sem dados sensiveis.",

    [string]$Agent = "marketplace_ia_agent",

    [switch]$CustomerUse
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
        & $Python "ops\k_os_external_api_sandbox.py" --mode smoke-test
    }
    "ShowPolicy" {
        & $Python "ops\k_os_external_api_sandbox.py" --mode show-policy
    }
    "Simulate" {
        $ArgsList = @(
            "ops\k_os_external_api_sandbox.py",
            "--mode", "simulate",
            "--provider", $Provider,
            "--use-case", $UseCase,
            "--prompt", $Prompt,
            "--agent", $Agent
        )

        if ($CustomerUse) {
            $ArgsList += "--customer-use"
        }

        & $Python @ArgsList
    }
}