# K-OS Agent Allowlisted Action Executor Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T21:50:15+00:00
- State committed: False
- Allowlist only: True
- Arbitrary command allowed: False
- Shell command allowed: False
- External publish enabled: False

## Metrics

- execution_count: 1
- validation_count: 1
- executed_count: 0
- blocked_count: 1
- arbitrary_command_count: 0
- shell_command_count: 0
- external_send_count: 0
- external_publish_count: 0
- external_provider_call_count: 0
- status_counts: {'blocked': 1}
- action_counts: {'safe_internal_noop': 1}

## Recent executions

- exec_b9502903779e | status=blocked | action=safe_internal_noop | agent=k_atlas_engineer

## Allowed actions

- safe_internal_noop
- cockpit_audit
- analytics_audit
- security_scan_staged
- memory_bus_audit
- context_api_audit
- agent_runtime_audit
- agent_queue_audit

## Required gates before action execution

- safe_route_exists
- safe_route_validated
- route_target_allowlisted
- approval_hash_present
- dry_run_evidence_hash_present
- arbitrary_command_blocked
- external_send_blocked
- external_publish_blocked
- pre_execution_evidence_created
- post_execution_evidence_created
- audit_event_recorded

## Next checkpoint

- 050 - K-Agent Execution Result Ledger Core