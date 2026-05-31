# K-OS Agent Replay and Forensics Viewer Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T22:02:37+00:00
- State committed: False
- Read only viewer: True
- Replay executes actions: False
- Raw payload storage allowed: False
- Approval token storage in reports allowed: False

## Metrics

- forensics_bundle_count: 1
- validation_count: 1
- bundle_created_count: 0
- validated_count: 0
- blocked_count: 1
- replay_execution_count: 0
- side_effect_count: 0
- approval_token_in_report_count: 0
- raw_payload_bundle_count: 0
- status_counts: {'blocked': 1}

## Recent bundles

- for_c43b46d433e5 | status=blocked | ledger=led_d89f1ee8fa5f | execution=exec_b9502903779e

## Required gates before forensics bundle

- ledger_record_exists
- ledger_record_validated
- ledger_record_hash_exists
- chain_hash_exists
- execution_evidence_hash_exists
- source_refs_sanitized
- approval_token_not_included
- raw_payload_not_included
- timeline_generated
- forensics_bundle_hash_created
- audit_event_recorded

## Next checkpoint

- 052 - K-Agent Incident Lockdown and Quarantine Core