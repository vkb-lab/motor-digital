$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
if (Test-Path ".\venv\Scripts\streamlit.exe") { $Streamlit = ".\venv\Scripts\streamlit.exe" } elseif (Test-Path ".\.venv\Scripts\streamlit.exe") { $Streamlit = ".\.venv\Scripts\streamlit.exe" } else { throw "Streamlit nao encontrado." }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\oi\Desktop\motor-digital'; & '$Streamlit' run 'pages\105_K_Atlas_MVP_Validation_Report.py' --server.port 8512 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8512"
Write-Host "K-Atlas MVP Validation Report aberto."
