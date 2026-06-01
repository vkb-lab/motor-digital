# K-OS Agent Recovery Final Gate Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:37:03+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- final_gate_record_count: 1
- validation_count: 1
- approved_for_future_manual_stub_count: 0
- blocked_count: 1
- revoked_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- status_counts: {'blocked': 1}

## Recent final gate records

- rfg_c42bd422642f | status=blocked | mode=block_execution | dry_run=missing

## Required gates before final gate

- recovery_dry_run_exists
- recovery_dry_run_hash_exists
- recovery_gate_exists
- recovery_plan_exists
- readiness_matrix_exists
- governance_summary_exists
- no_recovery_executed
- no_rollback_executed
- no_shell_executed
- final_gate_hash_created
- audit_event_recorded

## Next checkpoint

- 066 - K-Agent Recovery Manual Execution Stub Core