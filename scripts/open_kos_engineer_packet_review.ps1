param(
  [switch]$NoTick
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

if($NoTick){
  python scripts\run_phase69l_engineer_packet_review_console.py --no-tick
} else {
  python scripts\run_phase69l_engineer_packet_review_console.py
}
