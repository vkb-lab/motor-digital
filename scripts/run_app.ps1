$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $PSScriptRoot)
python scripts/init_kos.py
python -m streamlit run app.py

