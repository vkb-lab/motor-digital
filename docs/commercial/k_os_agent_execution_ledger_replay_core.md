# K-OS Agent Execution Ledger and Replay Core

Checkpoint 041.

Objetivo:

- registrar histórico de execuções dos agentes
- criar ledger auditável
- preservar hashes de entrada e saída
- permitir replay controlado de execuções
- comparar evidência de execução
- rastrear decisões
- preparar debug multiagente

## Regra central

O ledger é local e auditável.

Replay real só pode acontecer via Command Center e com aprovação humana.

Por padrão:

- replay em dry-run
- execução real exige approval
- estado bruto não vai para o GitHub
- relatórios públicos são sanitizados
- logs de auditoria não podem ser apagados
- envio externo bloqueado
- publicação externa bloqueada

## Estado local

local_secrets/k_os_agent_ledger/agent_execution_ledger.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/agent_ledger/latest_agent_execution_ledger_report.json
reports/agent_ledger/latest_agent_execution_evidence_snapshot.json
reports/agent_ledger/latest_agent_execution_replay_report.json

## Próximo checkpoint

042 - K-Memory Event Bus and Context Index Core