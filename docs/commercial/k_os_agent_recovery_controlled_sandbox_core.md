# K-OS Agent Recovery Controlled Execution Sandbox Core

Checkpoint 067.

Objetivo:

- criar sandbox controlada/local para ensaio futuro de recovery
- criar workspace local-only
- gerar manifest hash
- validar cadeia de recovery
- preparar review do operador
- manter execução real bloqueada

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

local_secrets/k_os_recovery_controlled_sandbox/agent_recovery_controlled_sandbox_state.json

Esse arquivo não vai para o GitHub.

## Workspace local

local_secrets/k_os_recovery_controlled_sandbox/workspaces/

Esse diretório não vai para o GitHub.

## Relatórios sanitizados

reports/recovery_controlled_sandbox/latest_agent_recovery_controlled_sandbox_report.json
reports/recovery_controlled_sandbox/latest_recovery_controlled_sandbox_record.json
reports/recovery_controlled_sandbox/latest_recovery_controlled_sandbox_validation_report.json

## Próximo checkpoint

068 - K-Agent Recovery Sandbox Operator Review Core