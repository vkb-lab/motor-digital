param(
  [switch]$Once
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

New-Item -ItemType Directory -Force "local_runtime\kos_chatgpt_bridge\drop" | Out-Null;

if($Once){
  python scripts\run_phase70d_chatgpt_bridge_drop_watcher.py --once --limit 5
} else {
  Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; python scripts\run_phase70d_chatgpt_bridge_drop_watcher.py --loop --poll-seconds 5 --limit 5`"";
  Start-Process (Resolve-Path "local_runtime\kos_chatgpt_bridge\drop");
}
