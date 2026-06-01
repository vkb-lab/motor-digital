# K-OS Agent Recovery Sandbox Operator Review Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T11:02:18+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- review_record_count: 1
- validation_count: 1
- review_acknowledged_blocked_count: 1
- changes_requested_count: 0
- archived_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- status_counts: {'review_acknowledged_blocked': 1}

## Recent reviews

- rsor_2a949d66345a | status=review_acknowledged_blocked | mode=acknowledge_blocked | blockers=10

## Required gates before sandbox review

- recovery_controlled_sandbox_exists
- recovery_controlled_sandbox_hash_exists
- workspace_manifest_hash_exists
- recovery_manual_stub_exists
- recovery_final_gate_exists
- recovery_dry_run_exists
- recovery_gate_exists
- recovery_plan_exists
- operator_review_recorded
- executive_summary_created
- no_recovery_executed
- no_rollback_executed
- no_shell_executed
- review_hash_created
- audit_event_recorded

## Next checkpoint

- 069 - K-Agent Recovery Governance Summary Core