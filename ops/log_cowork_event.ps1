param(
    [string]$Title = "Evento operacional K-Atlas",
    [string]$Details = "Evento registrado manualmente.",
    [string]$EventType = "manual"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

New-Item -ItemType Directory -Force -Path "memory\cowork_pilot_studio" | Out-Null
New-Item -ItemType Directory -Force -Path "reports\cowork_pilot_studio" | Out-Null

$Event = [ordered]@{
    event_id = [guid]::NewGuid().ToString()
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    event_type = $EventType
    title = $Title
    details = $Details
}

$Line = $Event | ConvertTo-Json -Compress -Depth 10
Add-Content -Path "memory\cowork_pilot_studio\story_events.jsonl" -Value $Line -Encoding UTF8

$Report = [ordered]@{
    ok = $true
    checkpoint = "67.5"
    name = "K-Atlas Cowork Event Logger"
    status = "event_logged"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    event = $Event
}

$Report | ConvertTo-Json -Depth 10 | Set-Content -Path "reports\cowork_pilot_studio\latest_cowork_event.json" -Encoding UTF8

Write-Host "Evento cowork registrado."
Write-Host "Titulo:" $Title
