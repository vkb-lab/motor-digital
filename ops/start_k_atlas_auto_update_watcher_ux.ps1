$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Project = "C:\Users\oi\Desktop\motor-digital"
$LogDir = Join-Path $Project "memory\auto_update_watcher"
$LogPath = Join-Path $LogDir "events.jsonl"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Show-KAtlasPopup {
    param(
        [string]$Message,
        [string]$Title = "K-Atlas Auto Update",
        [int]$Seconds = 4
    )

    try {
        $Shell = New-Object -ComObject WScript.Shell
        $null = $Shell.Popup($Message, $Seconds, $Title, 64)
    } catch {
        Write-Host $Message
    }
}

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

function Invoke-KAtlasInstaller {
    param(
        [System.IO.FileInfo]$File
    )

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

        Write-Host ""
        Write-Host "K-Atlas Auto Update detectou:"
        Write-Host $File.Name
        Write-Host "Movido para:"
        Write-Host $Destination
        Write-Host "Executando automaticamente..."
        Write-Host ""

        Write-KAtlasEvent -Type "installer_detected" -Payload @{
            source = $File.FullName
            destination = $Destination
            mode = "move_and_execute"
        }

        $Process = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Destination -Wait -PassThru -WindowStyle Normal

        if ($Process.ExitCode -eq 0) {
            Write-Host ""
            Write-Host "K-ATLAS AUTO UPDATE OK:"
            Write-Host $File.Name
            Write-Host ""

            Write-KAtlasEvent -Type "installer_executed_ok" -Payload @{
                file = $Destination
                exit_code = $Process.ExitCode
            }

            Show-KAtlasPopup -Message "Update executado com sucesso: $($File.Name)" -Seconds 4
        } else {
            Write-Host ""
            Write-Host "K-ATLAS AUTO UPDATE FALHOU:"
            Write-Host $File.Name
            Write-Host "ExitCode:" $Process.ExitCode
            Write-Host ""

            Write-KAtlasEvent -Type "installer_executed_error" -Payload @{
                file = $Destination
                exit_code = $Process.ExitCode
            }

            Show-KAtlasPopup -Message "Update falhou: $($File.Name). Veja o PowerShell." -Seconds 8
        }
    } catch {
        Write-Host ""
        Write-Host "Erro no Auto Update:"
        Write-Host $_.Exception.Message
        Write-Host ""

        Write-KAtlasEvent -Type "installer_exception" -Payload @{
            file = $File.FullName
            error = $_.Exception.Message
        }

        Show-KAtlasPopup -Message "Erro no Auto Update. Veja o PowerShell." -Seconds 8
    }
}

Write-Host "K-Atlas Auto Update Watcher UX iniciado."
Write-Host "Modo: mover + executar + popup"
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
            Invoke-KAtlasInstaller -File $File
        }
    }

    Start-Sleep -Seconds 2
}
