param(
    [switch]$ExecuteExisting
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    $Host.UI.RawUI.WindowTitle = "K-Atlas Auto Update Console"
} catch {}

$Project = "C:\Users\oi\Desktop\motor-digital"
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$StateDir = Join-Path $Project "memory\auto_update_watcher"
$ProcessedPath = Join-Path $StateDir "processed_hashes.txt"
$EventsPath = Join-Path $StateDir "events.jsonl"
$LatestPath = Join-Path $StateDir "latest_auto_update.json"
$AllowedRegex = "^(K_ATLAS_(CHECKPOINT|BATCH|FIX)_.+\.ps1)$"

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

function Write-Event {
    param(
        [string]$Type,
        [hashtable]$Payload
    )

    $Row = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        event_type = $Type
        payload = $Payload
    }

    $Row | ConvertTo-Json -Depth 20 -Compress | Add-Content -Path $EventsPath -Encoding UTF8
    $Row | ConvertTo-Json -Depth 20 | Set-Content -Path $LatestPath -Encoding UTF8
}

function Load-Processed {
    $Map = @{}

    if (Test-Path $ProcessedPath) {
        Get-Content $ProcessedPath -ErrorAction SilentlyContinue | ForEach-Object {
            $Line = $_
            if ($Line.Trim().Length -gt 0) {
                $Parts = $Line.Split("|")
                if ($Parts.Count -ge 1 -and $Parts[0]) {
                    $Map[$Parts[0]] = $true
                }
            }
        }
    }

    return $Map
}

function Mark-Processed {
    param(
        [string]$Hash,
        [string]$Name,
        [string]$Status
    )

    $Line = "$Hash|$Status|$((Get-Date).ToUniversalTime().ToString("o"))|$Name"
    Add-Content -Path $ProcessedPath -Value $Line -Encoding UTF8
}

function Wait-FileStable {
    param([string]$Path)

    for ($i = 0; $i -lt 12; $i++) {
        try {
            $A = Get-Item $Path -ErrorAction Stop
            $SizeA = $A.Length
            Start-Sleep -Milliseconds 700
            $B = Get-Item $Path -ErrorAction Stop
            $SizeB = $B.Length

            if ($SizeA -eq $SizeB -and $SizeB -gt 0) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }

    return $false
}

function Get-KAtlasInstallerFiles {
    $Roots = @($Downloads, $Project)
    $Files = @()

    foreach ($Root in $Roots) {
        if (Test-Path $Root) {
            $Files += Get-ChildItem -Path $Root -Filter "K_ATLAS_*.ps1" -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match $AllowedRegex }
        }
    }

    return $Files | Sort-Object LastWriteTime
}

function Invoke-KAtlasInstaller {
    param([System.IO.FileInfo]$File)

    if (-not (Wait-FileStable -Path $File.FullName)) {
        Write-Host "Arquivo ainda instavel, aguardando proximo ciclo:" $File.Name
        return
    }

    if ($File.Length -gt 5MB) {
        Write-Host "BLOQUEADO: instalador maior que 5MB:" $File.Name
        Write-Event -Type "auto_update_blocked_size" -Payload @{
            file = $File.FullName
            size = $File.Length
        }
        return
    }

    $Hash = (Get-FileHash -Path $File.FullName -Algorithm SHA256).Hash
    $Processed = Load-Processed

    if ($Processed.ContainsKey($Hash)) {
        return
    }

    $Destination = Join-Path $Project $File.Name

    try {
        if ($File.FullName -ne $Destination) {
            Copy-Item -Path $File.FullName -Destination $Destination -Force
        }

        Write-Host ""
        Write-Host "============================================================"
        Write-Host "K-ATLAS AUTO UPDATE DETECTADO"
        Write-Host "Arquivo:" $File.Name
        Write-Host "Origem:" $File.FullName
        Write-Host "Destino:" $Destination
        Write-Host "Hash:" $Hash
        Write-Host "Executando automaticamente..."
        Write-Host "============================================================"
        Write-Host ""

        Write-Event -Type "auto_update_started" -Payload @{
            file = $File.FullName
            destination = $Destination
            hash = $Hash
        }

        $Output = & powershell -NoProfile -ExecutionPolicy Bypass -File $Destination 2>&1
        $ExitCode = $LASTEXITCODE

        if ($Output) {
            $Output | ForEach-Object { Write-Host $_ }
        }

        if ($ExitCode -eq 0) {
            Mark-Processed -Hash $Hash -Name $File.Name -Status "success"

            Write-Host ""
            Write-Host "============================================================"
            Write-Host "AUTO UPDATE OK"
            Write-Host "Arquivo:" $File.Name
            Write-Host "Status: sucesso"
            Write-Host "============================================================"
            Write-Host ""

            Write-Event -Type "auto_update_success" -Payload @{
                file = $File.FullName
                destination = $Destination
                hash = $Hash
                exit_code = $ExitCode
            }
        } else {
            Mark-Processed -Hash $Hash -Name $File.Name -Status "failed"

            Write-Host ""
            Write-Host "============================================================"
            Write-Host "AUTO UPDATE FALHOU"
            Write-Host "Arquivo:" $File.Name
            Write-Host "ExitCode:" $ExitCode
            Write-Host "Comando manual:"
            Write-Host ('cd "' + $Project + '"; powershell -ExecutionPolicy Bypass -File ".\' + $File.Name + '"')
            Write-Host "============================================================"
            Write-Host ""

            Write-Event -Type "auto_update_failed" -Payload @{
                file = $File.FullName
                destination = $Destination
                hash = $Hash
                exit_code = $ExitCode
            }
        }
    } catch {
        Mark-Processed -Hash $Hash -Name $File.Name -Status "exception"

        Write-Host ""
        Write-Host "AUTO UPDATE ERROU COM EXCECAO"
        Write-Host $_.Exception.Message
        Write-Host ""

        Write-Event -Type "auto_update_exception" -Payload @{
            file = $File.FullName
            destination = $Destination
            hash = $Hash
            error = $_.Exception.Message
        }
    }
}

Write-Host "K-Atlas Auto Update Console ativo."
Write-Host "Vigiando Downloads e projeto."
Write-Host "Padrao permitido: K_ATLAS_CHECKPOINT_*.ps1, K_ATLAS_BATCH_*.ps1, K_ATLAS_FIX_*.ps1"
Write-Host "Ao baixar arquivo novo, ele sera copiado, executado e confirmado nesta tela."
Write-Host "Para parar: Ctrl + C"
Write-Host ""

if (-not $ExecuteExisting) {
    $Processed = Load-Processed

    foreach ($File in Get-KAtlasInstallerFiles) {
        try {
            $Hash = (Get-FileHash -Path $File.FullName -Algorithm SHA256).Hash
            if (-not $Processed.ContainsKey($Hash)) {
                Mark-Processed -Hash $Hash -Name $File.Name -Status "seed_existing"
            }
        } catch {}
    }

    Write-Host "Arquivos existentes foram marcados como conhecidos."
    Write-Host "Novos downloads serao executados automaticamente."
    Write-Host ""
} else {
    Write-Host "Modo ExecuteExisting ativo: arquivos existentes tambem podem ser processados."
    Write-Host ""
}

while ($true) {
    foreach ($File in Get-KAtlasInstallerFiles) {
        Invoke-KAtlasInstaller -File $File
    }

    Start-Sleep -Seconds 2
}