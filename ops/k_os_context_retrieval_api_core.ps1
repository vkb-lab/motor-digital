param(
    [ValidateSet("Init", "Catalog", "Retrieve", "Audit", "Serve", "Show")]
    [string]$Action = "Audit",

    [string]$Query = "",

    [string]$Domain = "",

    [string]$ModuleFilter = "",

    [string]$Event = "",

    [int]$Limit = 20,

    [string]$HostAddress = "127.0.0.1",

    [int]$Port = 8583
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
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode init
    }
    "Catalog" {
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode catalog
    }
    "Retrieve" {
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode retrieve --query $Query --domain $Domain --module-filter $ModuleFilter --event $Event --limit $Limit
    }
    "Audit" {
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode audit
    }
    "Serve" {
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode serve --host $HostAddress --port $Port
    }
    "Show" {
        & $Python "ops\k_os_context_retrieval_api_core.py" --mode show
    }
}