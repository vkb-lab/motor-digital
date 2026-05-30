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

Start-Process powershell -ArgumentList "-NoExit","-Command","cd 'C:\Users\oi\Desktop\motor-digital'; & '$Streamlit' run 'pages\106_K_Atlas_Download_Intake_UX.py' --server.port 8511 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8511"

Write-Host "Download Intake UX aberto em http://127.0.0.1:8511"
