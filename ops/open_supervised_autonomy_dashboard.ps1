$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\streamlit.exe") {
    $Streamlit = ".\venv\Scripts\streamlit.exe"
} elseif (Test-Path ".\.venv\Scripts\streamlit.exe") {
    $Streamlit = ".\.venv\Scripts\streamlit.exe"
} else {
    throw "Streamlit nao encontrado."
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$Streamlit`" run `"pages\98_K_Atlas_Supervised_Autonomy_Dashboard.py`" --server.port 8508 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8508"
Write-Host "K-Atlas Supervised Autonomy Dashboard aberto em http://127.0.0.1:8508"
