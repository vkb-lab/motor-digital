# K-OS Agent Permission Matrix

## Checkpoint 017

Objetivo:

- registrar quais agentes existem
- definir permissões explícitas
- impedir escalada silenciosa de autonomia
- documentar responsabilidade humana
- criar base para auditoria enterprise
- preparar K-Credential Vault e External API Sandbox

## Lei

Nenhum agente decide sozinho.

## Campos mínimos por agente

- agent_id
- name
- purpose
- human_owner
- risk_level
- autonomy_level
- can_read
- can_write
- can_execute_local
- can_commit
- can_push
- can_publish_external
- can_send_external
- can_access_credentials
- approval_gate_required
- required_gates
- forbidden_actions
- evidence_required

## Regras de bloqueio

- can_publish_external precisa ser false
- can_send_external precisa ser false
- can_access_credentials precisa ser false até existir K-Credential Vault
- agente com commit precisa Security Firewall
- agente high/critical precisa gate ou política automática
- toda ação crítica precisa evidência

## Conselhos iniciais

- K-OS Security Council
- K-OS AI Accountability Council
- K-OS Commercial Governance Council