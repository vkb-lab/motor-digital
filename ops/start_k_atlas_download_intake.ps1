$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Project = "C:\Users\oi\Desktop\motor-digital"
$LogDir = Join-Path $Project "memory\download_intake"
$LogPath = Join-Path $LogDir "events.jsonl"
$CommandPath = Join-Path $LogDir "latest_command.txt"
$LatestPath = Join-Path $LogDir "latest_download.json"
$FixedCommand = 'cd "C:\Users\oi\Desktop\motor-digital"; powershell -ExecutionPolicy Bypass -File ".\ops\k_next.ps1"'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Set-Content -Path $CommandPath -Value $FixedCommand -Encoding UTF8
Set-Clipboard -Value $FixedCommand

Write-Host "K-Atlas Download Intake Watcher iniciado."
Write-Host "Vigiando:" $Downloads
Write-Host "Destino:" $Project
Write-Host ""
Write-Host "Comando fixo copiado para area de transferencia:"
Write-Host $FixedCommand
Write-Host ""

$Seen = @{}

function Register-KAtlasDownload {
    param([System.IO.FileInfo]$File)

    if (-not $File.Exists) {
        return
    }

    if ($File.Name -notmatch "^(K_ATLAS_|k_atlas_).+\.ps1$") {
        return
    }

    Start-Sleep -Milliseconds 700

    $Destination = Join-Path $Project $File.Name

    try {
        Copy-Item -Path $File.FullName -Destination $Destination -Force
        Set-Content -Path $CommandPath -Value $FixedCommand -Encoding UTF8
        Set-Clipboard -Value $FixedCommand

        $Latest = [ordered]@{
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            source = $File.FullName
            destination = $Destination
            name = $File.Name
            command = $FixedCommand
        }

        $Latest | ConvertTo-Json -Depth 10 | Set-Content -Path $LatestPath -Encoding UTF8

        $Event = [ordered]@{
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            event_type = "k_atlas_download_ingested"
            source = $File.FullName
            destination = $Destination
            command = $FixedCommand
        }

        $Event | ConvertTo-Json -Depth 10 -Compress | Add-Content -Path $LogPath -Encoding UTF8

        Write-Host ""
        Write-Host "K-Atlas installer detectado:"
        Write-Host $File.Name
        Write-Host "Copiado para projeto."
        Write-Host "Comando fixo copiado:"
        Write-Host $FixedCommand
        Write-Host ""
    } catch {
        Write-Host "Falha ao processar:" $File.FullName
        Write-Host $_.Exception.Message
    }
}

while ($true) {
    Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^(K_ATLAS_|k_atlas_).+\.ps1$" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 20 |
        ForEach-Object {
            $Key = $_.FullName + "|" + $_.Length + "|" + $_.LastWriteTimeUtc.Ticks
            if (-not $Seen.ContainsKey($Key)) {
                $Seen[$Key] = $true
                Register-KAtlasDownload -File $_
            }
        }

    Start-Sleep -Seconds 2
}
