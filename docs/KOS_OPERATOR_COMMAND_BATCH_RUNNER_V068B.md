# K-OS Operator Command Batch Runner v0.68B

## Enviar lote seguro

powershell -ExecutionPolicy Bypass -File scripts\submit_kos_operator_command_batch.ps1 -Commands @("registrar item 1","registrar item 2") -RunNow

## Fluxo

Batch -> Operator Command Inbox -> Autonomy Command Bridge -> Job Intake -> Runner -> Output JSON.

## Regras

- Roteia somente para write_json_report.
- Respeita Kill Switch.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
