# K-OS Agent Runtime Supervisor Core

Checkpoint 040.

Objetivo:

- supervisionar execução dos agentes
- controlar runtime
- validar tarefas em andamento
- registrar heartbeat
- detectar falhas
- bloquear agente travado
- criar watchdog operacional
- preparar execução multiagente real

## Regra central

O Runtime Supervisor não executa comando arbitrário.

Ele observa, registra e bloqueia preventivamente.

Por padrão:

- heartbeat obrigatório
- watchdog ativo
- agente sem heartbeat vira stale
- agente com falha recorrente vira blocked
- fila de agentes é observada
- Command Center é obrigatório
- Permission Matrix é obrigatória
- envio externo bloqueado
- publicação externa bloqueada
- logs preservados

## Estado local

local_secrets/k_os_agent_runtime/agent_runtime_supervisor_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/agent_runtime/latest_agent_runtime_supervisor_report.json
reports/agent_runtime/latest_agent_runtime_watchdog_report.json
reports/agent_runtime/latest_agent_runtime_heartbeat_report.json

## Próximo checkpoint

041 - K-Agent Execution Ledger and Replay Core