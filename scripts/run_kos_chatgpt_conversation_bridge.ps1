param(
  [switch]$OpenConversation,
  [switch]$ProcessLatest,
  [switch]$OpenFolder
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ConversationUrl = "https://chatgpt.com/g/g-6a1835a4bd9c8191b314ede2fffc8923-k-atlas-engineer/c/6a1d9ced-417c-83e9-9d0c-16d3bf463616";
$DropDir = "local_runtime\kos_chatgpt_bridge\drop";

New-Item -ItemType Directory -Force $DropDir | Out-Null;

if($OpenConversation){
  Start-Process $ConversationUrl;
}

if($OpenFolder){
  Start-Process (Resolve-Path $DropDir);
}

if($ProcessLatest){
  $Latest = Get-ChildItem $DropDir -Filter "*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1;

  if(-not $Latest){
    throw "Nenhum pacote .txt encontrado em $DropDir"
  }

  Write-Host "[KOS] Processando pacote:";
  Write-Host $Latest.FullName;

  powershell -ExecutionPolicy Bypass -File scripts\run_kos_engineer_packet_oneclick.ps1 -File $Latest.FullName -NoQueueTick;
  python scripts\run_phase69l_engineer_packet_review_console.py;

  $Stamp = Get-Date -Format "yyyyMMdd_HHmmss";
  New-Item -ItemType Directory -Force "local_runtime\kos_chatgpt_bridge\processed" | Out-Null;
  Copy-Item $Latest.FullName "local_runtime\kos_chatgpt_bridge\processed\processed_$Stamp.txt" -Force;

  Write-Host "[KOS] Review:";
  Get-Content "local_runtime\kos_engineer_packet_review\latest_engineer_packet_review.json" -Encoding UTF8;
}
