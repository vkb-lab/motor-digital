# K-OS Agent Rollback Controlled Execution Sandbox Core

Checkpoint 058.

Objetivo:

- criar sandbox controlada de rollback
- simular ambiente de execução
- bloquear comandos destrutivos
- preservar evidências
- não executar shell
- não executar rollback real
- não alterar arquivos alvo
- não apagar dados
- não rodar git reset
- não rodar git force push

## Regra central

Este módulo cria uma sandbox governada, mas não executa rollback.

## Estado local

local_secrets/k_os_rollback_sandbox/agent_rollback_sandbox_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/rollback_sandbox/latest_agent_rollback_sandbox_report.json
reports/rollback_sandbox/latest_rollback_sandbox_record.json
reports/rollback_sandbox/latest_rollback_sandbox_validation_report.json

## Próximo checkpoint

059 - K-Agent Rollback Sandbox Report and Operator Review Core