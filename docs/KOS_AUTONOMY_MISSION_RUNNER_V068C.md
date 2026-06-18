# K-OS Autonomy Mission Runner v0.68C

## Executar missão segura

powershell -ExecutionPolicy Bypass -File scripts\run_kos_autonomy_mission.ps1 -MissionText "missao operacional" -Objectives @("objetivo 1","objetivo 2") -RunNow

## Fluxo

Mission -> Batch Runner -> Operator Command Inbox -> Command Bridge -> Job Intake -> Runner -> Output JSON.

## Regras

- Roteia somente para write_json_report.
- Respeita Kill Switch.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
