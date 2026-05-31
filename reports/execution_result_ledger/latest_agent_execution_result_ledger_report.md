# K-OS Agent Execution Result Ledger Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T21:56:52+00:00
- State committed: False
- Append only: True
- Raw payload storage allowed: False
- Approval token storage in reports allowed: False
- External publish enabled: False

## Metrics

- ledger_record_count: 1
- validation_count: 1
- recorded_count: 0
- validated_count: 0
- blocked_count: 1
- approval_token_in_report_count: 0
- raw_payload_record_count: 0
- external_send_count: 0
- external_publish_count: 0
- status_counts: {'blocked': 1}
- action_counts: {'safe_internal_noop': 1}

## Recent ledger records

- led_d89f1ee8fa5f | status=blocked | execution=exec_b9502903779e | action=safe_internal_noop

## Required gates before ledger record

- allowlisted_execution_exists
- allowlisted_execution_validated
- execution_evidence_hash_exists
- pre_execution_evidence_hash_exists
- post_execution_evidence_hash_exists
- approval_token_not_included
- no_arbitrary_command_executed
- no_shell_command_executed
- no_external_send_performed
- no_external_publish_performed
- ledger_record_hash_created
- audit_event_recorded

## Next checkpoint

- 051 - K-Agent Replay and Forensics Viewer Core