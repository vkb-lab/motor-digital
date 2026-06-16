$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"
$env:KOS_KAIZEN_DAEMON="true"
$env:KOS_KAIZEN_INTERVAL_SECONDS="900"
$env:KOS_KAIZEN_MAX_CYCLES="0"
python -m k_atlas.kaizen.orchestrator
