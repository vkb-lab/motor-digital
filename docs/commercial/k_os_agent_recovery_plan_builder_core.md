# K-OS Agent Recovery Plan Builder Core

Checkpoint 062.

Objetivo:

- criar plano de recovery governado
- usar readiness matrix
- usar governance summary
- usar operator review
- mapear precondições
- mapear blockers
- preparar approval gate futuro

## Regra central

Este módulo não executa recovery real.

Ele não:

- executa rollback
- apaga dados
- altera arquivos alvo
- roda git reset
- roda git force push
- executa shell
- chama API externa

## Estado local

local_secrets/k_os_recovery_plan_builder/agent_recovery_plan_builder_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/recovery_plan_builder/latest_agent_recovery_plan_builder_report.json
reports/recovery_plan_builder/latest_recovery_plan.json
reports/recovery_plan_builder/latest_recovery_plan_validation_report.json

## Próximo checkpoint

063 - K-Agent Recovery Approval Gate Core