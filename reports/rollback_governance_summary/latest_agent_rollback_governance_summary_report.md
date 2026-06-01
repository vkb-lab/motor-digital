# K-OS Agent Rollback Governance Summary Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:03:21+00:00
- State committed: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- summary_count: 1
- validation_count: 1
- closed_safe_count: 1
- closed_with_blockers_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- raw_payload_count: 0

## Recent summaries

- rgs_8ded4eeda1f9 | status=closed_safe | no_rollback=True | blockers=3

## Required gates before governance summary

- rollback_preparation_exists
- rollback_release_gate_exists
- rollback_dry_run_exists
- rollback_final_gate_exists
- manual_stub_exists
- controlled_sandbox_exists
- operator_review_exists
- evidence_chain_available
- rollback_execution_count_zero
- data_delete_count_zero
- target_file_modify_count_zero
- git_reset_count_zero
- git_force_push_count_zero
- summary_hash_created
- audit_event_recorded

## Next checkpoint

- 061 - K-Agent Recovery Readiness Matrix Core