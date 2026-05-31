# K-OS Agent Replay and Forensics Viewer Core

Checkpoint 051.

Objetivo:

- reconstruir trilha de execução governada
- visualizar timeline operacional
- conectar prompt, dry-run, aprovação, rota, execução e ledger
- verificar hashes e fontes
- gerar bundle forensics
- preparar resposta a incidentes

## Regra central

Replay Forensics é read-only.

Ele não:

- executa ações
- gera efeitos reais
- envia mensagens externas
- publica conteúdo externo
- chama provedores externos
- revela payload bruto
- revela token de aprovação

## Linha de replay

- context packet
- prompt package
- execution plan
- dry-run
- approval decision
- safe route
- allowlisted execution
- execution result ledger

## Estado local

local_secrets/k_os_replay_forensics/agent_replay_forensics_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/replay_forensics/latest_agent_replay_forensics_report.json
reports/replay_forensics/latest_replay_forensics_bundle.json
reports/replay_forensics/latest_replay_forensics_validation_report.json

## Próximo checkpoint

052 - K-Agent Incident Lockdown and Quarantine Core