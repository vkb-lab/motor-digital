# K-OS Agent Safe Execution Router Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T21:41:56+00:00
- State committed: False
- Allowlist only: True
- Router performs real execution: False
- Side effects performed by router: False
- External publish enabled: False

## Metrics

- route_count: 1
- validation_count: 1
- ready_route_count: 0
- blocked_route_count: 1
- real_execution_by_router_count: 0
- side_effect_by_router_count: 0
- external_send_count: 0
- external_publish_count: 0
- status_counts: {'blocked': 1}
- target_counts: {'cockpit_audit': 1}

## Recent routes

- route_2e1782e22c1c | status=blocked | target=cockpit_audit | agent=k_atlas_engineer

## Allowed route targets

- safe_internal_noop
- command_center_dry_route
- security_scan_staged
- analytics_audit
- cockpit_audit
- memory_bus_audit
- context_api_audit
- agent_runtime_audit
- agent_queue_audit

## Required gates before safe route

- approval_decision_exists
- approval_decision_validated
- approval_token_hash_exists
- dry_run_evidence_hash_exists
- route_target_allowlisted
- route_has_no_external_send
- route_has_no_external_publish
- route_has_no_side_effect
- permission_matrix_checked
- command_center_available
- audit_event_recorded

## Next checkpoint

- 049 - K-Agent Allowlisted Action Executor Core