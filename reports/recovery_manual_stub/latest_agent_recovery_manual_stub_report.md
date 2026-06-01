# K-OS Agent Recovery Manual Execution Stub Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:50:52+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- manual_stub_record_count: 1
- validation_count: 1
- intent_recorded_for_future_review_count: 0
- intent_blocked_count: 1
- intent_revoked_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- status_counts: {'intent_blocked': 1}

## Recent manual stub records

- rms_e5c9c9c0fc5a | status=intent_blocked | mode=record_blocked_intent | final_gate=blocked

## Required gates before manual stub

- recovery_final_gate_exists
- recovery_final_gate_hash_exists
- recovery_dry_run_exists
- recovery_gate_exists
- recovery_plan_exists
- readiness_matrix_exists
- governance_summary_exists
- operator_intent_recorded
- no_recovery_executed
- no_rollback_executed
- no_shell_executed
- stub_hash_created
- audit_event_recorded

## Next checkpoint

- 067 - K-Agent Recovery Controlled Execution Sandbox Core