$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Project = "C:\Users\oi\Desktop\motor-digital"
$Memory = Join-Path $Project "memory\auto_update_watcher"
$Processed = Join-Path $Memory "processed_installers"
$LogPath = Join-Path $Memory "events.jsonl"
$LatestRunLog = Join-Path $Memory "latest_run.log"
$LockPath = Join-Path $Memory "watcher_hidden.lock"

New-Item -ItemType Directory -Force -Path $Memory | Out-Null
New-Item -ItemType Directory -Force -Path $Processed | Out-Null

if (Test-Path $LockPath) {
    try {
        $OldPid = [int](Get-Content $LockPath -Raw)
        $OldProcess = Get-Process -Id $OldPid -ErrorAction SilentlyContinue
        if ($OldProcess) {
            exit 0
        }
    } catch {}
}

Set-Content -Path $LockPath -Value $PID -Encoding UTF8

$StartedAt = Get-Date
$Seen = @{}

Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^(K_ATLAS_|k_atlas_).+\.ps1$" } |
    ForEach-Object {
        $Seen[$_.FullName] = $true
    }

function Write-Event {
    param([string]$Type, [hashtable]$Payload)

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
        [string]$ClipboardText
    )

    try {
        Set-Clipboard -Value $ClipboardText
    } catch {}

    try {
        $Shell = New-Object -ComObject WScript.Shell
        $null = $Shell.Popup($Message, 0, "K-Atlas Auto Update", 64)
        Start-Sleep -Milliseconds 300
        $null = $Shell.AppActivate("ChatGPT")
        Start-Sleep -Milliseconds 300
    } catch {}
}

function Execute-Installer {
    param([System.IO.FileInfo]$File)

    if (-not $File.Exists) { return }
    if ($File.Name -notmatch "^(K_ATLAS_|k_atlas_).+\.ps1$") { return }

    Start-Sleep -Milliseconds 1200

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Destination = Join-Path $Project $File.Name
    $Archived = Join-Path $Processed ($Timestamp + "_" + $File.Name)

    try {
        if (Test-Path $Destination) {
            Remove-Item $Destination -Force -ErrorAction SilentlyContinue
        }

        Move-Item -Path $File.FullName -Destination $Destination -Force

        Write-Event -Type "installer_moved" -Payload @{
            source = $File.FullName
            destination = $Destination
        }

        "Executando: $Destination" | Set-Content -Path $LatestRunLog -Encoding UTF8

        Push-Location $Project
        powershell -NoProfile -ExecutionPolicy Bypass -File $Destination *> $LatestRunLog
        $ExitCode = $LASTEXITCODE
        Pop-Location

        Copy-Item -Path $Destination -Destination $Archived -Force -ErrorAction SilentlyContinue

        if ($ExitCode -eq 0) {
            Write-Event -Type "installer_ok" -Payload @{
                file = $Destination
                archived = $Archived
                exit_code = $ExitCode
            }

            Complete-ToChat -Message "Update OK:`n$($File.Name)`n`nClipboard: ok" -ClipboardText "ok"
        } else {
            Write-Event -Type "installer_error" -Payload @{
                file = $Destination
                archived = $Archived
                exit_code = $ExitCode
                log = $LatestRunLog
            }

            Complete-ToChat -Message "Update FALHOU:`n$($File.Name)`n`nVeja o log:`n$LatestRunLog`n`nClipboard: erro" -ClipboardText "erro"
        }
    } catch {
        Write-Event -Type "installer_exception" -Payload @{
            file = $File.FullName
            error = $_.Exception.Message
            log = $LatestRunLog
        }

        Complete-ToChat -Message "Erro no watcher:`n$($_.Exception.Message)`n`nClipboard: erro" -ClipboardText "erro"
    }
}

while ($true) {
    $Files = Get-ChildItem -Path $Downloads -Filter "*.ps1" -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "^(K_ATLAS_|k_atlas_).+\.ps1$" -and
            $_.LastWriteTime -gt $StartedAt.AddSeconds(-5)
        } |
        Sort-Object LastWriteTime

    foreach ($File in $Files) {
        $Key = $File.FullName + "|" + $File.LastWriteTimeUtc.Ticks + "|" + $File.Length

        if (-not $Seen.ContainsKey($Key)) {
            $Seen[$Key] = $true
            Execute-Installer -File $File
        }
    }

    Start-Sleep -Seconds 2
}
