# K-OS Mission Queue Processor v0.68D

## Enfileirar missão

powershell -ExecutionPolicy Bypass -File scripts\submit_kos_autonomy_mission_queue.ps1 -MissionText "missao" -Objectives @("objetivo 1","objetivo 2")

## Processar fila

powershell -ExecutionPolicy Bypass -File scripts\process_kos_autonomy_mission_queue.ps1 -Limit 5

## Regras

- Respeita Kill Switch.
- Usa Mission Runner 68C.
- Roteia somente para write_json_report.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
