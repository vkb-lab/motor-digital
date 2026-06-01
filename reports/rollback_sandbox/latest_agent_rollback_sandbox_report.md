# K-OS Agent Rollback Controlled Execution Sandbox Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T09:52:18+00:00
- State committed: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell commands: False

## Metrics

- sandbox_record_count: 1
- validation_count: 1
- sandbox_created_count: 0
- sandbox_blocked_by_governance_count: 1
- blocked_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- raw_payload_count: 0
- status_counts: {'sandbox_blocked_by_governance': 1}

## Recent sandbox records

- rxb_4111d5c730f1 | status=sandbox_blocked_by_governance | mode=safe_block | stub=rms_7921374b4857

## Required gates before sandbox

- manual_stub_exists
- manual_stub_hash_exists
- final_gate_exists
- dry_run_exists
- release_record_exists
- rollback_plan_exists
- incident_lockdown_exists
- forensics_bundle_available
- ledger_record_available
- destructive_commands_blocked
- sandbox_record_hash_created
- audit_event_recorded

## Next checkpoint

- 059 - K-Agent Rollback Sandbox Report and Operator Review Core