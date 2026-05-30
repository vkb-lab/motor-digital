$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CreatedNew = $false
$Mutex = New-Object System.Threading.Mutex($true, "KAtlasClipboardRunnerV41Guard", [ref]$CreatedNew)

if (-not $CreatedNew) {
    Write-Host "Ja existe um K-Atlas Clipboard Runner V4.1 Guard rodando."
    Read-Host "Pressione Enter para sair"
    exit 0
}

$Root = "C:\Users\oi\Desktop\motor-digital"
$MemoryDir = Join-Path $Root "memory\local_clipboard_runner"
$InboxDir = Join-Path $MemoryDir "approved_scripts"
$RejectedDir = Join-Path $MemoryDir "rejected_clipboard"
$LogDir = Join-Path $MemoryDir "logs"
$ReportDir = Join-Path $Root "reports\local_clipboard_runner"
$ReportPath = Join-Path $ReportDir "latest_local_clipboard_runner.json"
$Fence = ([string][char]96) + ([string][char]96) + ([string][char]96)

New-Item -ItemType Directory -Force -Path $InboxDir, $RejectedDir, $LogDir, $ReportDir | Out-Null

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Data
    )

    $Data | ConvertTo-Json -Depth 30 | Set-Content -Path $Path -Encoding UTF8
}

function Get-TextHash {
    param([string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Normalize-ScriptText {
    param([string]$Text)

    $Clean = $Text.Trim()

    if ($Clean.StartsWith($Fence)) {
        $Lines = @($Clean -split "\r?\n")

        if ($Lines.Count -gt 1) {
            $Lines = @($Lines | Select-Object -Skip 1)
        }

        if ($Lines.Count -gt 0 -and $Lines[$Lines.Count - 1].Trim() -eq $Fence) {
            if ($Lines.Count -gt 1) {
                $Lines = @($Lines | Select-Object -First ($Lines.Count - 1))
            } else {
                $Lines = @()
            }
        }

        $Clean = [string]::Join([Environment]::NewLine, $Lines).Trim()
    }

    return $Clean
}

function Test-KAtlasScript {
    param([string]$Text)

    $Reasons = @()
    $T = $Text.Trim()

    if ([string]::IsNullOrWhiteSpace($T)) {
        $Reasons += "clipboard_empty"
    }

    if ($T.Length -lt 120) {
        $Reasons += "too_short"
    }

    if ($T.Length -gt 80000) {
        $Reasons += "too_large_possible_mixed_or_truncated_block"
    }

    $StartsOk = $false
    $AllowedStarts = @(
        '$ErrorActionPreference',
        '[Console]::OutputEncoding',
        'param(',
        'cd "C:\Users\oi\Desktop\motor-digital"',
        "cd 'C:\Users\oi\Desktop\motor-digital'"
    )

    foreach ($Prefix in $AllowedStarts) {
        if ($T.StartsWith($Prefix)) {
            $StartsOk = $true
        }
    }

    if (-not $StartsOk) {
        $Reasons += "not_clean_powershell_start"
    }

    if ($T -notmatch "motor-digital" -and $T -notmatch "K-Atlas" -and $T -notmatch "k_atlas" -and $T -notmatch "Checkpoint" -and $T -notmatch "Stage") {
        $Reasons += "not_k_atlas_context"
    }

    $Blocked = @(
        "Pensou por",
        "Resultado esperado:",
        "A resposta do Claude foi interrompida",
        "Criou 5 arquivos",
        "Criou 8 arquivos",
        "contents have been truncated",
        "The file is too long",
        ($Fence + "text"),
        ($Fence + "python"),
        ($Fence + "html"),
        "selenium",
        "pyautogui",
        "Start-Process chrome",
        "chrome.exe --remote",
        "SendKeys",
        "mouse_event",
        "SetCursorPos",
        "Invoke-Expression",
        "iex ",
        "format.com",
        "cipher /w",
        "shutdown /s",
        "Remove-Item C:\",
        "Remove-Item -Recurse C:\"
    )

    $Lower = $T.ToLowerInvariant()

    foreach ($Term in $Blocked) {
        if ($Lower.Contains($Term.ToLowerInvariant())) {
            $Reasons += ("blocked_term:" + $Term)
        }
    }

    if ($T.Contains($Fence)) {
        $Reasons += "markdown_fence_inside_script"
    }

    return @{
        ok = ($Reasons.Count -eq 0)
        reasons = $Reasons
        length = $T.Length
    }
}

function Show-Preview {
    param([string]$Text)

    Write-Host ""
    Write-Host "Preview do bloco:"
    Write-Host "----------------"
    $Lines = $Text -split "\r?\n"
    foreach ($Line in ($Lines | Select-Object -First 20)) {
        Write-Host $Line
    }
    Write-Host "----------------"
    Write-Host ""
}

Write-Host ""
Write-Host "K-Atlas Local Clipboard Runner V4.1 Guard iniciado."
Write-Host "Modo: supervisionado rigido."
Write-Host "Aceita apenas bloco PowerShell limpo."
Write-Host "Bloqueia texto de chat, prompt misturado, bloco gigante e automacao insegura."
Write-Host "Para executar: copie bloco limpo e pressione A."
Write-Host "Para parar: Ctrl+C"
Write-Host ""

$LastHash = ""

while ($true) {
    Start-Sleep -Seconds 2

    try {
        $Raw = Get-Clipboard -Raw -ErrorAction Stop
    } catch {
        continue
    }

    if ([string]::IsNullOrWhiteSpace($Raw)) {
        continue
    }

    $Script = Normalize-ScriptText -Text $Raw
    $Hash = Get-TextHash -Text $Script

    if ($Hash -eq $LastHash) {
        continue
    }

    $LastHash = $Hash
    $Validation = Test-KAtlasScript -Text $Script
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    if (-not $Validation.ok) {
        $RejectedPath = Join-Path $RejectedDir "rejected_$Timestamp.txt"
        $Script | Set-Content -Path $RejectedPath -Encoding UTF8

        $Report = @{
            ok = $false
            runner = "v4_1_guard"
            status = "clipboard_rejected"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            reasons = $Validation.reasons
            length = $Validation.length
            rejected_path = $RejectedPath
            external_side_effects = "none"
        }

        Write-JsonFile -Path $ReportPath -Data $Report

        Write-Host ""
        Write-Host "Clipboard rejeitado pelo Runner V4.1."
        Write-Host "Motivos:" ($Validation.reasons -join ", ")
        Write-Host "Salvo em:" $RejectedPath
        Write-Host ""
        continue
    }

    Write-Host ""
    Write-Host "Novo bloco K-Atlas valido detectado."
    Write-Host "Tamanho:" $Script.Length "caracteres"
    Write-Host "Hash:" $Hash

    Show-Preview -Text $Script

    Write-Host "[A] Aprovar e executar"
    Write-Host "[S] Salvar sem executar"
    Write-Host "[I] Ignorar"

    $Choice = Read-Host "Escolha"

    $ScriptPath = Join-Path $InboxDir "approved_$Timestamp.ps1"
    $LogPath = Join-Path $LogDir "run_$Timestamp.log"

    if ($Choice -eq "I" -or $Choice -eq "i") {
        Write-Host "Ignorado."
        continue
    }

    $Script | Set-Content -Path $ScriptPath -Encoding UTF8

    if ($Choice -eq "S" -or $Choice -eq "s") {
        Write-Host "Salvo sem executar:" $ScriptPath

        Write-JsonFile -Path $ReportPath -Data @{
            ok = $true
            runner = "v4_1_guard"
            status = "saved_without_execution"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            script_path = $ScriptPath
            external_side_effects = "none"
        }

        continue
    }

    if ($Choice -eq "A" -or $Choice -eq "a") {
        Write-Host "Executando script aprovado..."
        Write-Host "Arquivo:" $ScriptPath
        Write-Host "Log:" $LogPath

        $Start = Get-Date
        $Output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath 2>&1
        $ExitCode = $LASTEXITCODE
        $Output | Out-File -FilePath $LogPath -Encoding UTF8
        $End = Get-Date

        Write-JsonFile -Path $ReportPath -Data @{
            ok = ($ExitCode -eq 0)
            runner = "v4_1_guard"
            status = if ($ExitCode -eq 0) { "executed" } else { "failed" }
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            started_at = $Start.ToUniversalTime().ToString("o")
            finished_at = $End.ToUniversalTime().ToString("o")
            exit_code = $ExitCode
            script_path = $ScriptPath
            log_path = $LogPath
            external_side_effects = "local_powershell_only"
            browser_automation_enabled = $false
            mouse_automation_enabled = $false
            human_approved = $true
        }

        if ($ExitCode -eq 0) {
            Write-Host "Execucao concluida com sucesso."
        } else {
            Write-Host "Execucao falhou. Veja o log:"
            Write-Host $LogPath
            Get-Content $LogPath -Tail 30 -ErrorAction SilentlyContinue
        }
    }
}
