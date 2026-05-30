$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Project = "C:\Users\oi\Desktop\motor-digital"
$LogDir = Join-Path $Project "memory\auto_update_watcher"
$LogPath = Join-Path $LogDir "events.jsonl"
$LatestRunLog = Join-Path $LogDir "latest_run.log"
$LockPath = Join-Path $LogDir "watcher.lock"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (Test-Path $LockPath) {
    try {
        $OldPid = [int](Get-Content $LockPath -Raw)
        $OldProcess = Get-Process -Id $OldPid -ErrorAction SilentlyContinue
        if ($OldProcess) {
            Write-Host "Watcher ja esta ativo. PID:" $OldPid
            exit 0
        }
    } catch {}
}

Set-Content -Path $LockPath -Value $PID -Encoding UTF8

function Write-KAtlasEvent {
    param(
        [string]$Type,
        [hashtable]$Payload
    )

    $Event = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        event_type = $Type
        payload = $Payload
    }

    $Event | ConvertTo-Json -Depth 20 -Compress | Add-Content -Path $LogPath -Encoding UTF8
}

function Complete-ToChat {
    param(
        [string]$Message,
        [string]$ClipboardText = "ok"
    )

    try {
        $Shell = New-Object -ComObject WScript.Shell
        $null = $Shell.Popup($Message, 0, "K-Atlas Auto Update", 64)
    } catch {
        Write-Host $Message
    }

    try {
        Set-Clipboard -Value $ClipboardText
    } catch {}

    try {
        $Shell = New-Object -ComObject WScript.Shell
        $null = $Shell.AppActivate("ChatGPT")
        Start-Sleep -Milliseconds 300
    } catch {}
}

function Invoke-KAtlasInstallerSilent {
    param([System.IO.FileInfo]$File)

    if (-not $File.Exists) {
        return
    }

    if ($File.Name -notmatch "^(K_ATLAS_|k_atlas_).+\.ps1$") {
        return
    }

    Start-Sleep -Milliseconds 1200

    $Destination = Join-Path $Project $File.Name

    try {
        if ($File.FullName -ne $Destination) {
            if (Test-Path $Destination) {
                Remove-Item $Destination -Force -ErrorAction SilentlyContinue
            }

            Move-Item -Path $File.FullName -Destination $Destination -Force
        }

        Set-Content -Path $LatestRunLog -Value "Executando: $Destination" -Encoding UTF8

        Write-KAtlasEvent -Type "installer_detected" -Payload @{
            source = $File.FullName
            destination = $Destination
            mode = "silent_move_execute_popup_focus_chat"
        }

        $Command = @"
cd "$Project"
powershell -NoProfile -ExecutionPolicy Bypass -File "$Destination" *> "$LatestRunLog"
exit `$LASTEXITCODE
"@

        $Process = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $Command -Wait -PassThru -WindowStyle Hidden

        if ($Process.ExitCode -eq 0) {
            Write-KAtlasEvent -Type "installer_executed_ok" -Payload @{
                file = $Destination
                exit_code = $Process.ExitCode
                log = $LatestRunLog
            }

            Complete-ToChat -Message "Update concluido com sucesso:`n$($File.Name)`n`nClipboard agora contem: ok" -ClipboardText "ok"
        } else {
            Write-KAtlasEvent -Type "installer_executed_error" -Payload @{
                file = $Destination
                exit_code = $Process.ExitCode
                log = $LatestRunLog
            }

            Complete-ToChat -Message "Update falhou:`n$($File.Name)`n`nVeja:`n$LatestRunLog`n`nClipboard agora contem: erro" -ClipboardText "erro"
        }
    } catch {
        Write-KAtlasEvent -Type "installer_exception" -Payload @{
            file = $File.FullName
            error = $_.Exception.Message
            log = $LatestRunLog
        }

        Complete-ToChat -Message "Erro no Auto Update:`n$($_.Exception.Message)`n`nClipboard agora contem: erro" -ClipboardText "erro"
    }
}

Write-Host "K-Atlas Auto Update Watcher SILENCIOSO ativo."
Write-Host "Modo:"
Write-Host "- move arquivo do Downloads"
Write-Host "- executa sem abrir janela extra"
Write-Host "- popup final"
Write-Host "- ao clicar OK, copia 'ok' e tenta focar ChatGPT"
Write-Host ""
Write-Host "Vigiando:" $Downloads
Write-Host "Destino:" $Project
Write-Host ""

$Seen = @{}

while ($true) {
    $Files = Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^(K_ATLAS_|k_atlas_).+\.ps1$" } |
        Sort-Object LastWriteTime -Descending

    foreach ($File in $Files) {
        $Key = $File.FullName + "|" + $File.LastWriteTimeUtc.Ticks + "|" + $File.Length

        if (-not $Seen.ContainsKey($Key)) {
            $Seen[$Key] = $true
            Invoke-KAtlasInstallerSilent -File $File
        }
    }

    Start-Sleep -Seconds 2
}
