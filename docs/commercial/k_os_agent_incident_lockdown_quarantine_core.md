# K-OS Agent Incident Lockdown and Quarantine Core

Checkpoint 052.

Objetivo:

- bloquear agente em incidente
- colocar execução em quarentena
- congelar rota, execução e ledger
- impedir novas ações
- registrar evidência de incidente
- preparar rollback e investigação

## Regra central

Lockdown seguro não apaga dados.

Ele apenas:

- cria registro de incidente
- cria quarentena local
- bloqueia novas ações
- bloqueia execução real
- preserva evidências
- exige revisão humana para liberação

## Bloqueios

- executar nova ação de agente
- executar ação real
- enviar mensagem externa
- publicar conteúdo externo
- chamar provedor externo
- apagar evidência
- apagar ledger
- liberar sem revisão humana
- exportar memória bruta
- exportar segredo

## Estado local

local_secrets/k_os_incident_lockdown/agent_incident_lockdown_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/incident_lockdown/latest_agent_incident_lockdown_report.json
reports/incident_lockdown/latest_incident_lockdown_record.json
reports/incident_lockdown/latest_incident_lockdown_validation_report.json

## Próximo checkpoint

053 - K-Agent Rollback Preparation Core