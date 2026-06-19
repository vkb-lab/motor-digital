param(
  [ValidateSet("menu","status","dashboard","user-dashboard","market-radar","operator-command","mission","queue-mission")]
  [string]$Mode = "menu",

  [string]$Text = "registrar healthcheck operacional via launcher",

  [string]$MissionText = "missao operacional via launcher",

  [string[]]$Objectives = @("registrar runtime","registrar autonomia segura")
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

function Show-Header {
  Clear-Host;
  Write-Host "K-OS User Launcher";
  Write-Host "Root: $Root";
  Write-Host "";
}

function Show-Runtime {
  powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action status;
}

function Open-Dashboard {
  Start-Process "http://localhost:8501";
}

function Open-UserDashboard {
  Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; streamlit run pages\KOS_User_Launcher.py --server.port 8517`"";
  Start-Sleep -Seconds 2;
  Start-Process "http://localhost:8517";
}

function Run-MarketRadar {
  python scripts\run_phase69a_agent_os_market_radar.py;
}

function Run-OperatorCommand {
  param([string]$CommandText)
  powershell -ExecutionPolicy Bypass -File scripts\submit_kos_operator_command.ps1 -Text $CommandText -RunNow;
}

function Run-Mission {
  param([string]$Mission, [string[]]$Goals)
  powershell -ExecutionPolicy Bypass -File scripts\run_kos_autonomy_mission.ps1 -MissionText $Mission -Objectives $Goals -RunNow;
}

function Queue-Mission {
  param([string]$Mission, [string[]]$Goals)
  powershell -ExecutionPolicy Bypass -File scripts\submit_kos_autonomy_mission_queue.ps1 -MissionText $Mission -Objectives $Goals;
}

switch($Mode){
  "status" { Show-Runtime; exit 0 }
  "dashboard" { Open-Dashboard; exit 0 }
  "user-dashboard" { Open-UserDashboard; exit 0 }
  "market-radar" { Run-MarketRadar; exit 0 }
  "operator-command" { Run-OperatorCommand -CommandText $Text; exit 0 }
  "mission" { Run-Mission -Mission $MissionText -Goals $Objectives; exit 0 }
  "queue-mission" { Queue-Mission -Mission $MissionText -Goals $Objectives; exit 0 }
}

while($true){
  Show-Header;
  Write-Host "1 - Ver status do K-OS";
  Write-Host "2 - Abrir dashboard principal";
  Write-Host "3 - Abrir launcher web";
  Write-Host "4 - Enviar comando seguro";
  Write-Host "5 - Executar missao segura";
  Write-Host "6 - Enfileirar missao";
  Write-Host "7 - Gerar Agent OS Market Radar";
  Write-Host "8 - Mostrar comandos Kill Switch";
  Write-Host "0 - Sair";
  Write-Host "";

  $Choice = Read-Host "Escolha uma opcao";

  if($Choice -eq "0"){ break }

  try {
    switch($Choice){
      "1" { Show-Runtime }
      "2" { Open-Dashboard; Write-Host "Dashboard principal aberto." }
      "3" { Open-UserDashboard; Write-Host "Launcher web aberto." }
      "4" {
        $Cmd = Read-Host "Digite o comando seguro";
        if([string]::IsNullOrWhiteSpace($Cmd)){ $Cmd = "registrar healthcheck operacional via launcher" }
        Run-OperatorCommand -CommandText $Cmd;
      }
      "5" {
        $Mission = Read-Host "Digite a missao";
        if([string]::IsNullOrWhiteSpace($Mission)){ $Mission = "missao operacional via launcher" }
        $Goal1 = Read-Host "Objetivo 1";
        $Goal2 = Read-Host "Objetivo 2";
        Run-Mission -Mission $Mission -Goals @($Goal1,$Goal2);
      }
      "6" {
        $Mission = Read-Host "Digite a missao para fila";
        if([string]::IsNullOrWhiteSpace($Mission)){ $Mission = "missao em fila via launcher" }
        Queue-Mission -Mission $Mission -Goals @("registrar evento de fila","registrar autonomia segura");
      }
      "7" { Run-MarketRadar }
      "8" {
        Write-Host "";
        Write-Host "Parada emergencial:";
        Write-Host 'powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action engage -Reason "operator emergency stop"';
        Write-Host "";
        Write-Host "Reativar:";
        Write-Host 'powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action disengage -Reason "operator restore" -RestartRuntime';
      }
      default { Write-Host "Opcao invalida." }
    }
  } catch {
    Write-Host "ERRO:";
    Write-Host $_.Exception.Message;
  }

  Write-Host "";
  Read-Host "Pressione ENTER para continuar";
}
