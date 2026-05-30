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

Write-Host "Abrindo Secure Local API Dashboard..."
Write-Host "URL: http://127.0.0.1:8504"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$Streamlit`" run `"pages\93_K_Atlas_Secure_Local_API_Dashboard.py`" --server.port 8504 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8504"
