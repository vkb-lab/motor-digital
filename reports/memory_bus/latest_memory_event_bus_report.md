# K-OS Memory Event Bus and Context Index Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T20:36:44+00:00
- State committed: False
- Sanitized reports only: True
- Raw payload storage in reports: False
- External publish enabled: False

## Metrics

- event_count: 989
- context_item_count: 20
- context_ok_count: 18
- missing_context_count: 1
- query_count: 1
- domain_count: 15
- raw_payload_included: False

## Domain summary

- memory_bus: events=1 | context=0 | ok=0 | missing=0
- agent_ledger: events=11 | context=1 | ok=1 | missing=0
- command_center: events=892 | context=1 | ok=1 | missing=0
- agent_runtime: events=21 | context=1 | ok=1 | missing=0
- agent_queue: events=10 | context=1 | ok=1 | missing=0
- cockpit: events=6 | context=1 | ok=1 | missing=0
- analytics: events=12 | context=1 | ok=1 | missing=0
- roadmap: events=6 | context=1 | ok=1 | missing=0
- product: events=5 | context=1 | ok=1 | missing=0
- support: events=5 | context=2 | ok=2 | missing=0
- customer_ops: events=4 | context=2 | ok=1 | missing=1
- commercial: events=16 | context=4 | ok=4 | missing=0
- security: events=0 | context=2 | ok=1 | missing=0
- governance: events=0 | context=1 | ok=1 | missing=0
- audit: events=0 | context=1 | ok=1 | missing=0

## Latest events

- 2026-05-31T20:36:43+00:00 | memory_bus | memory_bus | memory_bus.audit_generated
- 2026-05-31T20:32:33+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:32:32+00:00 | command_center | command_center | command_center.action_dry_run
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.execution_recorded
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.replay_completed
- 2026-05-31T20:32:31+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:31:18+00:00 | command_center | command_center | command_center.action_dry_run
- 2026-05-31T20:31:18+00:00 | agent_ledger | agent_ledger | agent_ledger.replay_completed
- 2026-05-31T20:31:18+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:31:17+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:31:17+00:00 | agent_ledger | agent_ledger | agent_ledger.execution_recorded
- 2026-05-31T20:31:17+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:31:17+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:25:40+00:00 | agent_runtime | agent_runtime | agent_runtime.heartbeat
- 2026-05-31T20:25:40+00:00 | agent_runtime | agent_runtime | agent_runtime.watchdog_completed
- 2026-05-31T20:25:40+00:00 | agent_runtime | agent_runtime | agent_runtime.watchdog_completed
- 2026-05-31T20:25:40+00:00 | agent_runtime | agent_runtime | agent_runtime.audit_generated
- 2026-05-31T20:25:39+00:00 | agent_runtime | agent_runtime | agent_runtime.watchdog_completed
- 2026-05-31T20:25:39+00:00 | agent_runtime | agent_runtime | agent_runtime.audit_generated
- 2026-05-31T20:25:39+00:00 | agent_runtime | agent_runtime | agent_runtime.agent_registered
- 2026-05-31T20:25:39+00:00 | agent_runtime | agent_runtime | agent_runtime.watchdog_completed
- 2026-05-31T20:25:39+00:00 | agent_runtime | agent_runtime | agent_runtime.audit_generated
- 2026-05-31T20:23:42+00:00 | agent_runtime | agent_runtime | agent_runtime.watchdog_completed
- 2026-05-31T20:23:42+00:00 | agent_runtime | agent_runtime | agent_runtime.audit_generated

## Required gates before external memory export

- sanitized_snapshot_generated
- raw_payload_removed
- payload_hashes_only
- security_review
- human_operator_approval

## Blocked actions

- commit_raw_memory_index
- export_raw_events
- store_customer_identifiable_payload_in_report
- delete_memory_events
- delete_context_index
- send_external_message
- publish_external_content
- call_external_provider
- bypass_sanitization

## Next checkpoint

- 043 - K-Context Retrieval API Core