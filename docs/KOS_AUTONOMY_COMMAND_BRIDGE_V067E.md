# K-OS Autonomy Command Bridge v0.67E

## Criar comando autonomo seguro

powershell -ExecutionPolicy Bypass -File scripts\create_kos_autonomy_command.ps1 -CommandText "registrar healthcheck operacional"

## Fluxo

CommandText -> command record -> autonomous job intake -> runner -> output JSON.

## Regras

- Roteia somente para write_json_report.
- Respeita Kill Switch.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
