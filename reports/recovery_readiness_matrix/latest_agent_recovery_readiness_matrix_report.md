# K-OS Agent Recovery Readiness Matrix Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:07:47+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- matrix_count: 1
- validation_count: 1
- controlled_ready_count: 0
- review_required_count: 1
- limited_ready_count: 0
- not_ready_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- level_counts: {'review_required': 1}

## Recent matrices

- rrm_46e71134fb25 | score=100 | level=review_required | risk=medium

## Required gates before recovery readiness

- rollback_governance_summary_exists
- rollback_governance_summary_hash_exists
- checkpoints_053_060_available
- operator_review_exists
- sandbox_review_exists
- evidence_chain_available
- no_real_rollback_executed
- no_data_deleted
- no_target_files_modified
- no_git_reset_executed
- no_force_push_executed
- readiness_score_created
- audit_event_recorded

## Next checkpoint

- 062 - K-Agent Recovery Plan Builder Core