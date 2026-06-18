# K-OS Operator Command Inbox v0.68A

## Enviar comando operacional seguro

powershell -ExecutionPolicy Bypass -File scripts\submit_kos_operator_command.ps1 -Text "registrar healthcheck operacional" -RunNow

## Fluxo

Operator Text -> Operator Inbox -> Autonomy Command Bridge -> Job Intake -> Runner -> Output JSON.

## Regras

- Roteia somente para write_json_report.
- Respeita Kill Switch.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
