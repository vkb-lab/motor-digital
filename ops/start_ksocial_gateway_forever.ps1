$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = "C:\Users\oi\Desktop\motor-digital"
cd $ProjectRoot

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    python -m venv venv
    $Python = ".\venv\Scripts\python.exe"
}

$env:PYTHONPATH = $ProjectRoot

while ($true) {
    Write-Host "K-Social Gateway iniciando em http://localhost:8501"
    Write-Host "Celular na mesma rede: use o Network URL mostrado pelo Streamlit."
    Write-Host "Pressione Ctrl+C para parar manualmente."

    & $Python -m pip install -r requirements.txt

    & $Python -m streamlit run app_ksocial_gateway.py `
        --server.port 8501 `
        --server.address 0.0.0.0 `
        --server.enableCORS false `
        --server.enableXsrfProtection false `
        --server.runOnSave true

    Write-Host "K-Social Gateway caiu ou foi parado. Reiniciando em 10 segundos..."
    Start-Sleep -Seconds 10
}