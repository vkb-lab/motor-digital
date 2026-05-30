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

$Page = "pages\908_K_Uni_Marketplace_IA_Public_Capture.py"
$Port = 8538

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\oi\Desktop\motor-digital'; & '$Streamlit' run '$Page' --server.port $Port --server.address 127.0.0.1"
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:$Port"

Write-Host "CAPTURA PUBLICA CONTROLADA ABERTA."
Write-Host "URL: http://127.0.0.1:$Port"