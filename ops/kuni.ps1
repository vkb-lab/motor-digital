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

$Port = 8520

$PreferredPages = @(
    "pages\999_K_Atlas_K_Uni_Master_Dashboard.py",
    "pages\543_K_Atlas_KUniMainConsoleDashboard.py",
    "pages\538_K_Atlas_KUniMainOperatorConsole.py",
    "pages\523_K_Atlas_KUniLauncherDashboard.py",
    "pages\508_K_Atlas_KUniValidationDashboard.py",
    "pages\100_K_Atlas_Local_OS_Release_Capsule.py"
)

$Page = $null

foreach ($Candidate in $PreferredPages) {
    if (Test-Path $Candidate) {
        $Page = Resolve-Path $Candidate
        break
    }
}

if (-not $Page) {
    $Page = Get-ChildItem ".\pages" -Filter "*KUni*Dashboard*.py" -File |
        Sort-Object Name -Descending |
        Select-Object -First 1
}

if (-not $Page) {
    throw "Nenhuma pagina K-Uni encontrada."
}

$Session = [ordered]@{
    opened_at = (Get-Date).ToUniversalTime().ToString("o")
    page = $Page.ToString()
    port = $Port
    url = "http://127.0.0.1:$Port"
    status = "opening"
}

New-Item -ItemType Directory -Force -Path "memory\k_uni_runtime" | Out-Null
$Session | ConvertTo-Json -Depth 10 | Set-Content -Path "memory\k_uni_runtime\latest_open_session.json" -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\oi\Desktop\motor-digital'; & '$Streamlit' run '$Page' --server.port $Port --server.address 127.0.0.1"
Start-Process "http://127.0.0.1:$Port"

Write-Host "K-UNI MASTER ABERTO."
Write-Host "URL: http://127.0.0.1:$Port"
Write-Host "Pagina:" $Page
