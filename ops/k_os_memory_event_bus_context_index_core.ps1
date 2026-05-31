param(
    [ValidateSet("Init", "BuildIndex", "Search", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Query = ""
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
        & $Python "ops\k_os_memory_event_bus_context_index_core.py" --mode init
    }
    "BuildIndex" {
        & $Python "ops\k_os_memory_event_bus_context_index_core.py" --mode build-index
    }
    "Search" {
        & $Python "ops\k_os_memory_event_bus_context_index_core.py" --mode search --query $Query
    }
    "Audit" {
        & $Python "ops\k_os_memory_event_bus_context_index_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_memory_event_bus_context_index_core.py" --mode show
    }
}