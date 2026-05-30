$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\\Users\\oi\\Desktop\\motor-digital"

if (Test-Path ".\\venv\\Scripts\\streamlit.exe") {
    $Streamlit = ".\\venv\\Scripts\\streamlit.exe"
} elseif (Test-Path ".\\.venv\\Scripts\\streamlit.exe") {
    $Streamlit = ".\\.venv\\Scripts\\streamlit.exe"
} else {
    throw "Streamlit nao encontrado no ambiente virtual."
}

Write-Host "Abrindo K-Atlas Remote Assist Readiness..."
Write-Host "URL: http://127.0.0.1:8505"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$Streamlit`" run `"pages\\78_K_Atlas_Remote_Assist_Readiness.py`" --server.port 8505 --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:8505"

Write-Host "K-Atlas Remote Assist Readiness aberto"
