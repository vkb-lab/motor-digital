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

Write-Host "Abrindo K-Atlas Local Control Plane..."
Write-Host "URL: http://127.0.0.1:8505"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$Streamlit`" run `"pages\77_K_Atlas_Local_Control_Plane.py`" --server.port 8505 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8505"
