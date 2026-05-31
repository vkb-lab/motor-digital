# K-OS Agent Incident Lockdown and Quarantine Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T22:07:51+00:00
- State committed: False
- New agent actions blocked: False
- Real execution blocked: False
- Lockdown deletes data: False
- Human review required to release: True

## Metrics

- incident_count: 1
- validation_count: 1
- active_quarantine_count: 0
- blocked_count: 1
- released_count: 0
- data_delete_count: 0
- raw_payload_incident_count: 0
- approval_token_in_report_count: 0
- status_counts: {'blocked': 1}
- severity_counts: {'SEV3': 1}

## Recent incidents

- inc_66fb283052e6 | quarantine=qua_4b0cb9303592 | status=blocked | severity=SEV3

## Required gates before lockdown

- incident_reason_present
- scope_present
- severity_present
- forensics_bundle_available
- ledger_record_available
- execution_evidence_hash_available
- quarantine_record_created
- lockdown_record_hash_created
- release_requires_human_review
- audit_event_recorded

## Next checkpoint

- 053 - K-Agent Rollback Preparation Core