# K-OS Agent Orchestration Queue Core

Checkpoint 039.

Objetivo:

- criar fila de orquestração de agentes
- registrar tarefas para agentes
- priorizar execuções
- controlar status
- bloquear agente sem permissão
- ligar fila ao Command Center
- preparar execução multiagente governada

## Regra central

A fila não executa comando arbitrário.

Toda execução deve passar pelo Command Center Action Router.

Por padrão:

- dry-run ativo
- aprovação exigida
- agente precisa estar autorizado
- ação precisa existir na allowlist
- envio externo bloqueado
- publicação externa bloqueada
- logs preservados

## Estado local

local_secrets/k_os_agent_queue/agent_orchestration_queue.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/agent_queue/latest_agent_orchestration_queue_report.json
reports/agent_queue/latest_agent_queue_snapshot.json
reports/agent_queue/latest_agent_dispatch_report.json

## Próximo checkpoint

040 - K-Agent Runtime Supervisor Core