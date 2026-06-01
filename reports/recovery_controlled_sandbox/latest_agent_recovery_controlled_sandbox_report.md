# K-OS Agent Recovery Controlled Execution Sandbox Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:56:04+00:00
- State committed: False
- Workspace committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- sandbox_record_count: 1
- validation_count: 1
- sandbox_created_local_only_count: 0
- sandbox_blocked_by_governance_count: 1
- sandbox_review_required_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- status_counts: {'sandbox_blocked_by_governance': 1}

## Recent sandbox records

- rcs_ad461bff2e64 | status=sandbox_blocked_by_governance | mode=safe_block | final_gate=blocked

## Required gates before recovery sandbox

- recovery_manual_stub_exists
- recovery_manual_stub_hash_exists
- recovery_final_gate_exists
- recovery_dry_run_exists
- recovery_gate_exists
- recovery_plan_exists
- readiness_matrix_exists
- governance_summary_exists
- local_workspace_manifest_created
- workspace_hash_created
- no_recovery_executed
- no_rollback_executed
- no_shell_executed
- sandbox_hash_created
- audit_event_recorded

## Next checkpoint

- 068 - K-Agent Recovery Sandbox Operator Review Core