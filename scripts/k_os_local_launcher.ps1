$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:GIT_PAGER = "cat"

$Root = Split-Path -Parent $PSScriptRoot
cd $Root

Write-Host "K-OS LOCAL LAUNCHER"
Write-Host "Modo: inicializacao local do cockpit Streamlit."

$PythonExe = "python"
$PythonPrefix = @()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $PythonPrefix = @("-3")
    } else {
        throw "Python nao encontrado no PATH."
    }
}

$Entrypoint = @("app.py", "streamlit_app.py", "Home.py") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Entrypoint) {
    throw "Nenhum entrypoint Streamlit encontrado. Esperado: app.py, streamlit_app.py ou Home.py."
}

function Get-FreePort {
    param([int]$StartPort = 8501)

    for ($Port = $StartPort; $Port -lt ($StartPort + 100); $Port++) {
        $Listener = $null
        try {
            $Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
            $Listener.Start()
            $Listener.Stop()
            return $Port
        } catch {
            if ($Listener) {
                $Listener.Stop()
            }
        }
    }

    throw "Nenhuma porta livre encontrada a partir de $StartPort."
}

$Port = Get-FreePort -StartPort 8501
Write-Host "Abrindo K-OS em http://localhost:$Port"

$StreamlitArgs = @()
$StreamlitArgs += $PythonPrefix
$StreamlitArgs += @(
    "-m", "streamlit", "run", $Entrypoint,
    "--server.port", "$Port",
    "--server.headless", "false"
)

& $PythonExe @StreamlitArgs