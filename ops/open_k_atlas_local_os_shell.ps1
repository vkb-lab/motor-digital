$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
if (Test-Path ".\venv\Scripts\streamlit.exe") { $Streamlit = ".\venv\Scripts\streamlit.exe" } elseif (Test-Path ".\.venv\Scripts\streamlit.exe") { $Streamlit = ".\.venv\Scripts\streamlit.exe" } else { throw "Streamlit nao encontrado." }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$Streamlit`" run `"pages\83_K_Atlas_Local_OS_Shell.py`" --server.port 8507 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8507"
Write-Host "K-Atlas Local OS Shell aberto em http://127.0.0.1:8507"
