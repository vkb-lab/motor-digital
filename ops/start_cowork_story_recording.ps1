param(
    [ValidateSet("none", "ffmpeg", "obs")]
    [string]$Mode = "none"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$SessionDir = "memory\cowork_pilot_studio\recordings\session_$Timestamp"
New-Item -ItemType Directory -Force -Path $SessionDir | Out-Null

$Session = [ordered]@{
    ok = $true
    checkpoint = "67.5"
    name = "K-Atlas Cowork Story Recording"
    status = "recording_session_prepared"
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    mode = $Mode
    session_dir = $SessionDir
    external_side_effects = "local_recording_only"
}

$Session | ConvertTo-Json -Depth 10 | Set-Content -Path "$SessionDir\session.json" -Encoding UTF8

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\log_cowork_event.ps1" -Title "Sessao de gravacao preparada" -Details "Modo: $Mode" -EventType "recording"

if ($Mode -eq "none") {
    Write-Host "Sessao preparada sem iniciar gravacao."
    Write-Host "Pasta:" $SessionDir
    exit 0
}

if ($Mode -eq "ffmpeg") {
    $FFmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue

    if (-not $FFmpeg) {
        Write-Host "FFmpeg nao encontrado no PATH."
        Write-Host "Sessao criada, mas gravacao nao iniciada."
        Write-Host "Pasta:" $SessionDir
        exit 0
    }

    $VideoPath = Join-Path (Resolve-Path $SessionDir) "cowork_screen.mp4"
    $Cmd = "& ffmpeg -y -f gdigrab -framerate 12 -i desktop -c:v libx264 -preset ultrafast -pix_fmt yuv420p `"$VideoPath`""

    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Cmd

    Write-Host "Gravacao ffmpeg iniciada em nova janela."
    Write-Host "Para parar: foque a janela do ffmpeg e pressione q."
    Write-Host "Arquivo:" $VideoPath
    exit 0
}

if ($Mode -eq "obs") {
    $Candidates = @(
        "C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        "C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe"
    )

    $ObsPath = $null

    foreach ($Candidate in $Candidates) {
        if (Test-Path $Candidate) {
            $ObsPath = $Candidate
            break
        }
    }

    if (-not $ObsPath) {
        Write-Host "OBS nao encontrado."
        Write-Host "Sessao criada, mas gravacao nao iniciada."
        Write-Host "Pasta:" $SessionDir
        exit 0
    }

    Start-Process -FilePath $ObsPath -ArgumentList "--startrecording"

    Write-Host "OBS iniciado com tentativa de gravacao."
    Write-Host "Confira visualmente o OBS."
    exit 0
}
