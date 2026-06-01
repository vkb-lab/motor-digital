# K-OS Agent Rollback Manual Execution Stub Core

- Status: audit_generated
- OK: True
- Generated at: 2026-06-01T09:46:48+00:00
- State committed: False
- Executes rollback: False
- Deletes data: False
- Modifies files: False
- Runs git reset: False
- Runs git force push: False

## Metrics

- manual_stub_record_count: 1
- validation_count: 1
- intent_recorded_blocked_count: 0
- intent_blocked_count: 1
- intent_revoked_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- raw_payload_count: 0
- status_counts: {'intent_blocked': 1}

## Recent manual stub records

- rms_7921374b4857 | status=intent_blocked | mode=block_intent | final_gate=rfg_8e6fb9e9116b

## Required gates before manual stub

- rollback_final_gate_exists
- rollback_final_gate_hash_exists
- rollback_dry_run_exists
- rollback_dry_run_hash_exists
- rollback_release_record_exists
- rollback_plan_exists
- incident_lockdown_exists
- forensics_bundle_available
- ledger_record_available
- operator_intent_present
- destructive_actions_blocked
- manual_stub_record_hash_created
- audit_event_recorded

## Next checkpoint

- 058 - K-Agent Rollback Controlled Execution Sandbox Core