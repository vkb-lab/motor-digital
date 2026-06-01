# K-OS Agent Recovery Approval Gate Core

Checkpoint 063.

Objetivo:

- registrar aprovacao, bloqueio ou revogacao para recovery futuro
- exigir operador humano
- exigir confirmação explícita
- manter token local fora do GitHub
- manter recovery real bloqueado

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

local_secrets/k_os_recovery_gate/agent_recovery_gate_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/recovery_gate/latest_agent_recovery_gate_report.json
reports/recovery_gate/latest_recovery_gate_record.json
reports/recovery_gate/latest_recovery_gate_validation_report.json

## Próximo checkpoint

064 - K-Agent Recovery Dry Run Simulator Core