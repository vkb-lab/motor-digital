param(
    [switch]$SmokeTest
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = "C:\Users\oi\Desktop\motor-digital"
$MemoryDir = Join-Path $Root "memory\local_clipboard_runner"
$ReportsDir = Join-Path $Root "reports\local_clipboard_runner"
$InboxDir = Join-Path $MemoryDir "approved_scripts"
$LogDir = Join-Path $MemoryDir "logs"
$StatePath = Join-Path $MemoryDir "state.json"
$ReportPath = Join-Path $ReportsDir "latest_local_clipboard_runner.json"

New-Item -ItemType Directory -Force -Path $MemoryDir, $ReportsDir, $InboxDir, $LogDir | Out-Null

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Data
    )

    $Data | ConvertTo-Json -Depth 20 | Set-Content -Path $Path -Encoding UTF8
}

function Get-TextHash {
    param([string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Test-KAtlasClipboardCommand {
    param([string]$Text)

    $Reasons = @()

    if ([string]::IsNullOrWhiteSpace($Text)) {
        $Reasons += "clipboard_empty"
    }

    if ($Text.Length -lt 80) {
        $Reasons += "too_short"
    }

    if ($Text -notmatch "motor-digital" -and $Text -notmatch "Checkpoint" -and $Text -notmatch "k_atlas") {
        $Reasons += "not_k_atlas_context"
    }

    $BlockedPatterns = @(
        "selenium",
        "pyautogui",
        "Start-Process chrome",
        "chrome.exe --remote",
        "SendKeys",
        "mouse_event",
        "SetCursorPos",
        "Invoke-Expression",
        "iex ",
        "Remove-Item C:\",
        "Remove-Item -Recurse C:\",
        "format.com",
        "cipher /w",
        "shutdown /s"
    )

    foreach ($Pattern in $BlockedPatterns) {
        if ($Text.ToLowerInvariant().Contains($Pattern.ToLowerInvariant())) {
            $Reasons += "blocked_pattern:$Pattern"
        }
    }

    return @{
        ok = ($Reasons.Count -eq 0)
        reasons = $Reasons
    }
}

if ($SmokeTest) {
    $Smoke = @{
        ok = $true
        checkpoint = "local_clipboard_runner"
        status = "smoke_test_ok"
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
        external_side_effects = "none"
        real_execution_enabled = $false
        browser_automation_enabled = $false
        mouse_automation_enabled = $false
    }

    Write-JsonFile -Path $ReportPath -Data $Smoke
    Write-Host "Smoke test OK: Local Clipboard Runner instalado."
    exit 0
}

Write-Host ""
Write-Host "K-Atlas Local Clipboard Runner iniciado."
Write-Host "Modo: supervisionado."
Write-Host "Uso: copie um bloco PowerShell do ChatGPT. O runner detecta e pede aprovacao."
Write-Host "Seguranca: sem mouse, sem navegador, sem execucao sem aprovacao."
Write-Host "Para parar: Ctrl+C"
Write-Host ""

$LastHash = ""

while ($true) {
    Start-Sleep -Seconds 2

    try {
        $Clip = Get-Clipboard -Raw -ErrorAction Stop
    } catch {
        continue
    }

    if ([string]::IsNullOrWhiteSpace($Clip)) {
        continue
    }

    $Hash = Get-TextHash -Text $Clip

    if ($Hash -eq $LastHash) {
        continue
    }

    $LastHash = $Hash
    $Validation = Test-KAtlasClipboardCommand -Text $Clip

    if (-not $Validation.ok) {
        $Report = @{
            ok = $false
            status = "clipboard_ignored"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            reasons = $Validation.reasons
            hash = $Hash
        }

        Write-JsonFile -Path $ReportPath -Data $Report
        continue
    }

    Write-Host ""
    Write-Host "Novo bloco K-Atlas detectado no clipboard."
    Write-Host "Tamanho:" $Clip.Length "caracteres"
    Write-Host ""
    Write-Host "[A] Aprovar e executar"
    Write-Host "[S] Salvar sem executar"
    Write-Host "[I] Ignorar"
    $Choice = Read-Host "Escolha"

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $ScriptPath = Join-Path $InboxDir "approved_$Timestamp.ps1"
    $LogPath = Join-Path $LogDir "run_$Timestamp.log"

    if ($Choice -eq "I" -or $Choice -eq "i") {
        Write-Host "Ignorado."
        continue
    }

    $Clip | Set-Content -Path $ScriptPath -Encoding UTF8

    if ($Choice -eq "S" -or $Choice -eq "s") {
        $Report = @{
            ok = $true
            status = "saved_without_execution"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            script_path = $ScriptPath
            hash = $Hash
            external_side_effects = "none"
        }

        Write-JsonFile -Path $ReportPath -Data $Report
        Write-Host "Salvo sem executar:" $ScriptPath
        continue
    }

    if ($Choice -eq "A" -or $Choice -eq "a") {
        Write-Host "Executando script aprovado..."
        Write-Host "Arquivo:" $ScriptPath
        Write-Host "Log:" $LogPath

        $Start = Get-Date

        powershell -ExecutionPolicy Bypass -File $ScriptPath *> $LogPath
        $ExitCode = $LASTEXITCODE

        $End = Get-Date

        $Report = @{
            ok = ($ExitCode -eq 0)
            status = if ($ExitCode -eq 0) { "executed" } else { "failed" }
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            started_at = $Start.ToUniversalTime().ToString("o")
            finished_at = $End.ToUniversalTime().ToString("o")
            exit_code = $ExitCode
            script_path = $ScriptPath
            log_path = $LogPath
            hash = $Hash
            external_side_effects = "local_powershell_only"
            browser_automation_enabled = $false
            mouse_automation_enabled = $false
            human_approved = $true
        }

        Write-JsonFile -Path $ReportPath -Data $Report

        if ($ExitCode -eq 0) {
            Write-Host "Execucao concluida com sucesso."
        } else {
            Write-Host "Execucao falhou. Veja o log:"
            Write-Host $LogPath
        }
    }
}
