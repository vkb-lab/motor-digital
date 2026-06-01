# K-OS Agent Recovery Governance Summary Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T11:10:36+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- summary_count: 1
- validation_count: 1
- closed_safe_count: 0
- closed_with_review_required_count: 1
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0

## Recent summaries

- rgs2_ccd59093b101 | status=closed_with_review_required | evidence=False | blockers=33

## Required gates before recovery governance summary

- recovery_readiness_matrix_exists
- recovery_plan_exists
- recovery_gate_exists
- recovery_dry_run_exists
- recovery_final_gate_exists
- recovery_manual_stub_exists
- recovery_controlled_sandbox_exists
- recovery_sandbox_review_exists
- evidence_chain_available
- no_recovery_executed
- no_rollback_executed
- no_data_deleted
- no_target_files_modified
- no_git_reset_executed
- no_force_push_executed
- no_shell_executed
- summary_hash_created
- audit_event_recorded

## Next checkpoint

- 070 - K-Agent Recovery Layer Closure Core