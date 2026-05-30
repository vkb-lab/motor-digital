$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Project = "C:\Users\oi\Desktop\motor-digital"
$LogDir = Join-Path $Project "memory\download_intake"
$LogPath = Join-Path $LogDir "events.jsonl"
$CommandPath = Join-Path $LogDir "latest_command.txt"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "K-Atlas Download Intake Watcher iniciado."
Write-Host "Vigiando:" $Downloads
Write-Host "Destino:" $Project
Write-Host ""
Write-Host "Quando baixar K_ATLAS_*.ps1, ele sera copiado para o projeto."
Write-Host "O comando de execucao sera copiado automaticamente."
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

    Start-Sleep -Milliseconds 800

    $Destination = Join-Path $Project $File.Name

    try {
        Copy-Item -Path $File.FullName -Destination $Destination -Force

        $Command = 'cd "C:\Users\oi\Desktop\motor-digital"; powershell -ExecutionPolicy Bypass -File ".\' + $File.Name + '"'
        Set-Content -Path $CommandPath -Value $Command -Encoding UTF8
        Set-Clipboard -Value $Command

        $Event = [ordered]@{
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            event_type = "k_atlas_download_ingested"
            source = $File.FullName
            destination = $Destination
            command = $Command
        }

        $Event | ConvertTo-Json -Depth 10 -Compress | Add-Content -Path $LogPath -Encoding UTF8

        Write-Host ""
        Write-Host "K-Atlas installer detectado:"
        Write-Host $File.Name
        Write-Host "Copiado para:"
        Write-Host $Destination
        Write-Host ""
        Write-Host "Comando copiado para area de transferencia:"
        Write-Host $Command
        Write-Host ""
    } catch {
        Write-Host "Falha ao processar:" $File.FullName
        Write-Host $_.Exception.Message
    }
}

Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue | ForEach-Object {
    $Key = $_.FullName + "|" + $_.LastWriteTimeUtc.Ticks
    if (-not $Seen.ContainsKey($Key)) {
        $Seen[$Key] = $true
        Register-KAtlasDownload -File $_
    }
}

while ($true) {
    Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 20 | ForEach-Object {
        $Key = $_.FullName + "|" + $_.LastWriteTimeUtc.Ticks
        if (-not $Seen.ContainsKey($Key)) {
            $Seen[$Key] = $true
            Register-KAtlasDownload -File $_
        }
    }

    Start-Sleep -Seconds 2
}
