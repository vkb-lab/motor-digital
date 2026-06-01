# K-OS Agent Rollback Sandbox Report and Operator Review Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T09:57:42+00:00
- State committed: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- review_count: 1
- validation_count: 1
- review_recorded_count: 1
- changes_requested_count: 0
- archived_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- raw_payload_count: 0
- status_counts: {'review_recorded': 1}
- decision_counts: {'acknowledge_blocked': 1}

## Recent reviews

- rsr_d73f9b355302 | status=review_recorded | decision=acknowledge_blocked | sandbox=rxb_4111d5c730f1

## Required gates before operator review

- sandbox_record_exists
- sandbox_record_hash_exists
- manual_stub_exists
- final_gate_exists
- dry_run_exists
- release_record_exists
- rollback_plan_exists
- blockers_consolidated
- operator_review_recorded
- review_record_hash_created
- audit_event_recorded

## Next checkpoint

- 060 - K-Agent Rollback Governance Summary Core