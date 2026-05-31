# K-OS Command Center Action Router

Checkpoint 038.

Objetivo:

- criar roteador central de ações
- executar comandos controlados
- abrir caminho para automação operacional
- rodar auditorias
- atualizar relatórios
- bloquear ações perigosas
- exigir approval gate
- registrar execução auditável

## Regra central

O Command Center não aceita comando arbitrário.

Ele só executa ações registradas em allowlist.

Por padrão:

- dry-run ativo
- envio externo bloqueado
- publicação externa bloqueada
- shell arbitrário bloqueado
- ações médias/altas exigem aprovação
- tudo gera evento e relatório

## Estado local

local_secrets/k_os_command_center/action_router_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/command_center/latest_command_center_action_router_report.json
reports/command_center/latest_action_catalog.json
reports/command_center/latest_action_execution_report.json

## Próximo checkpoint

039 - K-Agent Orchestration Queue Core