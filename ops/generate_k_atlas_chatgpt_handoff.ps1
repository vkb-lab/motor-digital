$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = "C:\Users\oi\Desktop\motor-digital"
$MemoryDir = Join-Path $Root "memory\chatgpt_handoff"
$ReportsDir = Join-Path $Root "reports\chatgpt_handoff"
$PromptPath = Join-Path $MemoryDir "next_prompt_for_chatgpt.md"
$ReportPath = Join-Path $ReportsDir "latest_chatgpt_handoff.json"
$LogPath = Join-Path $ReportsDir "latest_chatgpt_handoff.log"

New-Item -ItemType Directory -Force -Path $MemoryDir, $ReportsDir | Out-Null

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Data
    )

    $Data | ConvertTo-Json -Depth 20 | Set-Content -Path $Path -Encoding UTF8
}

function Test-FileExists {
    param([string]$Path)

    if (Test-Path $Path) {
        return $true
    }

    return $false
}

cd $Root

$GitStatusRaw = git status --short 2>$null
$GitDirty = -not [string]::IsNullOrWhiteSpace($GitStatusRaw)

$GitLogRaw = git log --oneline -8 2>$null
$GitLogLines = @()
if ($GitLogRaw) {
    $GitLogLines = $GitLogRaw -split "`n"
}

$KnownReports = @(
    "reports/planning_approval_packager/latest_planning_approval_packager.json",
    "reports/command_center_planning_runner/latest_command_center_planning_runner.json",
    "reports/command_center_mission_intake/latest_command_center_mission_intake.json",
    "reports/operator_mission_queue/latest_operator_mission_queue.json",
    "reports/service_readiness_matrix/latest_service_readiness_matrix.json",
    "reports/local_clipboard_runner/latest_local_clipboard_runner.json"
)

$ReportSignals = @()

foreach ($Relative in $KnownReports) {
    $Full = Join-Path $Root $Relative

    if (Test-Path $Full) {
        try {
            $Json = Get-Content $Full -Raw -Encoding UTF8 | ConvertFrom-Json
            $ReportSignals += @{
                path = $Relative
                exists = $true
                status = $Json.status
                ok = $Json.ok
                name = $Json.name
                generated_at = $Json.generated_at
            }
        } catch {
            $ReportSignals += @{
                path = $Relative
                exists = $true
                status = "read_error"
                ok = $false
            }
        }
    } else {
        $ReportSignals += @{
            path = $Relative
            exists = $false
            status = "missing"
            ok = $false
        }
    }
}

$Stage = "63"
$Prompt = @"
K-Atlas Engineer, contexto operacional atual:

O K-Atlas OS está rodando localmente.
O Runner supervisionado V3 já está ativo.
Eu consigo copiar um bloco PowerShell seu, pressionar A no runner, e ele executa com log.
A etapa 62 foi executada com sucesso pelo runner.
Agora quero continuar a evolução operacional.

Estado resumido:
- Execução local supervisionada funcionando
- GitHub segue como memória persistente
- Streamlit local segue ativo
- Sem publicação automática
- Sem deploy automático
- Sem API externa real
- Sem token em texto puro
- Sem automação insegura de navegador
- Sem mouse automático por enquanto
- Todo próximo passo deve gerar arquivo, log ou relatório

Missão:
Gerar a próxima etapa operacional do K-Atlas, a partir da etapa $Stage.

Objetivo imediato:
Criar o centro de decisão humana para aprovar, negar ou pedir ajustes nos pacotes gerados pelo Planning Approval Packager.

Regras obrigatórias:
- responder em português
- entregar um único bloco PowerShell completo
- compatível com Windows PowerShell
- usar UTF-8
- incluir smoke test
- incluir commit
- incluir push
- não usar navegador automático
- não usar mouse automático
- não chamar API externa real
- não publicar nada
- não fazer deploy automático
- manter governança humana
- cada ação importante deve gerar arquivo, log ou relatório

Fluxo desejado:
1. Eu copio seu bloco.
2. O Runner V3 detecta.
3. Eu pressiono A.
4. O K-Atlas executa.
5. O sistema gera relatório.
6. Depois gero novo prompt de continuidade para colar aqui.
"@

$Prompt | Set-Content -Path $PromptPath -Encoding UTF8

$ClipboardOk = $false
try {
    Set-Clipboard -Value $Prompt
    $ClipboardOk = $true
} catch {
    $ClipboardOk = $false
}

$Report = @{
    ok = $true
    name = "K-Atlas ChatGPT Handoff Generator"
    status = "prompt_generated"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    prompt_path = $PromptPath
    report_path = $ReportPath
    clipboard_updated = $ClipboardOk
    git_dirty = $GitDirty
    git_log = $GitLogLines
    report_signals = $ReportSignals
    external_side_effects = "clipboard_only"
    browser_automation_enabled = $false
    mouse_automation_enabled = $false
    real_execution_enabled = $false
    next_action = "colar o prompt gerado no ChatGPT para receber o proximo bloco operacional"
}

Write-JsonFile -Path $ReportPath -Data $Report

$Log = @"
K-Atlas ChatGPT Handoff Generator
Status: prompt_generated
Prompt: $PromptPath
Report: $ReportPath
Clipboard updated: $ClipboardOk
Generated at: $($Report.generated_at)
"@

$Log | Set-Content -Path $LogPath -Encoding UTF8

Write-Host "Prompt de continuidade gerado."
Write-Host "Arquivo:" $PromptPath
Write-Host "Relatorio:" $ReportPath
Write-Host "Clipboard atualizado:" $ClipboardOk
Write-Host "Agora cole no ChatGPT para continuar."
