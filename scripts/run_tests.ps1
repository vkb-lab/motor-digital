$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $PSScriptRoot)
python scripts/healthcheck.py
python -m pytest -q

