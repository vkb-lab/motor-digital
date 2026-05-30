param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Project = "C:\Users\oi\Desktop\motor-digital"
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Memory = Join-Path $Project "memory\download_intake"
$StatePath = Join-Path $Memory "state.json"
$LatestPath = Join-Path $Memory "latest_download.json"
$ExecutedPath = Join-Path $Memory "executed_installers.jsonl"
$Command = 'cd "C:\Users\oi\Desktop\motor-digital"; powershell -ExecutionPolicy Bypass -File ".\ops\k_next.ps1"'

New-Item -ItemType Directory -Force -Path $Memory | Out-Null
Set-Clipboard -Value $Command
Set-Content -Path (Join-Path $Memory "latest_command.txt") -Value $Command -Encoding UTF8

cd $Project

function Get-InstallerKey {
    param([System.IO.FileInfo]$File)
    return "$($File.Name)|$($File.Length)|$($File.LastWriteTimeUtc.Ticks)"
}

function Get-ExecutedKeys {
    $Keys = @{}
    if (Test-Path $ExecutedPath) {
        Get-Content $ExecutedPath -Encoding UTF8 | ForEach-Object {
            if ($_.Trim()) {
                try {
                    $Row = $_ | ConvertFrom-Json
                    if ($Row.key) {
                        $Keys[$Row.key] = $true
                    }
                } catch {}
            }
        }
    }
    return $Keys
}

function Register-Executed {
    param(
        [System.IO.FileInfo]$File,
        [string]$Status,
        [int]$ExitCode
    )

    $Row = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        key = Get-InstallerKey -File $File
        name = $File.Name
        path = $File.FullName
        status = $Status
        exit_code = $ExitCode
    }

    $Row | ConvertTo-Json -Compress -Depth 10 | Add-Content -Path $ExecutedPath -Encoding UTF8
}

function Get-InstallStartTime {
    if (Test-Path $StatePath) {
        try {
            $State = Get-Content $StatePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($State.installed_at) {
                return [datetime]::Parse($State.installed_at).ToUniversalTime()
            }
        } catch {}
    }

    return (Get-Date).ToUniversalTime().AddDays(-1)
}

function Get-PendingInstaller {
    $InstalledAt = Get-InstallStartTime
    $Executed = Get-ExecutedKeys

    $Candidates = @()

    foreach ($Root in @($Downloads, $Project)) {
        if (Test-Path $Root) {
            $Candidates += Get-ChildItem -Path $Root -Filter "K_ATLAS*.ps1" -File -ErrorAction SilentlyContinue
        }
    }

    $Candidates = $Candidates |
        Where-Object {
            $_.Name -match "^(K_ATLAS_|k_atlas_)" -and
            $_.Name -ne "K_ATLAS_CHECKPOINT_106_INSTALL.ps1" -and
            $_.LastWriteTimeUtc -ge $InstalledAt.AddMinutes(-1)
        } |
        Sort-Object LastWriteTimeUtc -Descending

    foreach ($File in $Candidates) {
        $Key = Get-InstallerKey -File $File
        if ($Force -or -not $Executed.ContainsKey($Key)) {
            return $File
        }
    }

    return $null
}

$Installer = Get-PendingInstaller

if (-not $Installer) {
    Write-Host ""
    Write-Host "K-Atlas k_next"
    Write-Host "Nenhum instalador K_ATLAS novo pendente."
    Write-Host ""
    Write-Host "Fluxo correto:"
    Write-Host "1. Baixe o proximo K_ATLAS_*.ps1 no chat"
    Write-Host "2. Volte para este PowerShell"
    Write-Host "3. Rode sempre:"
    Write-Host $Command
    Write-Host ""
    exit 0
}

$Destination = Join-Path $Project $Installer.Name

if ($Installer.DirectoryName -ne $Project) {
    Copy-Item -Path $Installer.FullName -Destination $Destination -Force
    $Installer = Get-Item $Destination
}

$Latest = [ordered]@{
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    source = $Installer.FullName
    destination = $Destination
    name = $Installer.Name
    command = $Command
}

$Latest | ConvertTo-Json -Depth 10 | Set-Content -Path $LatestPath -Encoding UTF8

Write-Host ""
Write-Host "K-Atlas k_next"
Write-Host "Instalador pendente detectado:"
Write-Host $Installer.Name
Write-Host ""

if ($DryRun) {
    Write-Host "Dry-run: nada executado."
    Write-Host "Para executar, rode sem -DryRun:"
    Write-Host $Command
    exit 0
}

Write-Host "Executando no PowerShell principal..."
Write-Host ""

powershell -ExecutionPolicy Bypass -File $Installer.FullName
$Exit = $LASTEXITCODE

if ($Exit -ne 0) {
    Register-Executed -File $Installer -Status "failed" -ExitCode $Exit
    throw "Instalador falhou com exit code $Exit"
}

Register-Executed -File $Installer -Status "completed" -ExitCode 0

if (Test-Path ".\ops\log_cowork_event.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\log_cowork_event.ps1" -Title "k_next executou instalador" -Details $Installer.Name -EventType "installer_executed"
}

Write-Host ""
Write-Host "K_NEXT EXECUTADO COM SUCESSO."
Write-Host "Instalador:" $Installer.Name
