# K-OS Agent Recovery Plan Builder Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T10:12:44+00:00
- State committed: False
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- plan_count: 1
- validation_count: 1
- prepared_review_required_count: 0
- blocked_review_required_count: 1
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- status_counts: {'plan_blocked_review_required': 1}

## Recent plans

- rpb_be687cf9460f | status=plan_blocked_review_required | readiness=review_required | risk=medium

## Required gates before recovery plan

- recovery_readiness_matrix_exists
- readiness_matrix_hash_exists
- rollback_governance_summary_exists
- operator_review_exists
- evidence_chain_available
- risk_level_available
- recovery_scope_defined
- future_execution_marked_manual_only
- plan_hash_created
- audit_event_recorded

## Next checkpoint

- 063 - K-Agent Recovery Approval Gate Core