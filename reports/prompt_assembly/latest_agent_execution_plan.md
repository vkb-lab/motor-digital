# K-OS Agent Execution Plan

- Plan ID: plan_68e35c606d06
- Agent: k_atlas_engineer
- Task: closure_prompt_assembly_validation
- Action: cockpit_audit
- Objective: Atualizar e auditar o cockpit executivo do K-OS usando contexto operacional sanitizado.
- Dry run: True
- Requires approval for real execution: True

## Steps

- 1 | validar_contexto | gate=context_packet_validated
- 2 | confirmar_permissao | gate=agent_permission_and_command_center_gate
- 3 | executar_dry_run | gate=dry_run_completed
- 4 | registrar_evidencia | gate=audit_event_recorded

## Blocked actions

- external_send
- external_publish
- raw_payload_use
- secret_use
- real_execution_without_approval