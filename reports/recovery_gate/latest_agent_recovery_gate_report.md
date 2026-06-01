# K-OS Agent Recovery Approval Gate Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:20:07+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- gate_record_count: 1
- validation_count: 1
- approved_count: 0
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

## Recent gate records

- rag_6b7618acfa6d | status=blocked | mode=block_recovery | plan=rpb_be687cf9460f

## Required gates before recovery gate

- recovery_plan_exists
- recovery_plan_hash_exists
- readiness_matrix_exists
- operator_confirmation_present
- gate_record_hash_created
- local_token_not_exported
- no_recovery_executed
- no_rollback_executed
- audit_event_recorded

## Next checkpoint

- 064 - K-Agent Recovery Dry Run Simulator Core