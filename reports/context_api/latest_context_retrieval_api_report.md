# K-OS Context Retrieval API Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T20:45:24+00:00
- Local only: True
- Bind address: 127.0.0.1
- Default port: 8583
- Raw payload return allowed: False
- External publish enabled: False
- Memory source available: True

## Metrics

- Events: 999
- Context items: 20
- Domains: 15
- Endpoints: 6

## Domains

- memory_bus: events=11 | context=0
- agent_ledger: events=11 | context=1
- command_center: events=892 | context=1
- agent_runtime: events=21 | context=1
- agent_queue: events=10 | context=1
- cockpit: events=6 | context=1
- analytics: events=12 | context=1
- roadmap: events=6 | context=1
- product: events=5 | context=1
- support: events=5 | context=2
- customer_ops: events=4 | context=2
- commercial: events=16 | context=4
- security: events=0 | context=2
- governance: events=0 | context=1
- audit: events=0 | context=1

## Recent retrievals

- ret_b7f9219562b7 | query=agent | events=10 | contexts=5
- ret_24d1005c1883 | query=agent | events=10 | contexts=5
- ret_7432b524fc8d | query=agent | events=10 | contexts=1

## Required gates before external context export

- local_retrieval_completed
- raw_payload_removed
- payload_hashes_only
- security_review
- human_operator_approval

## Blocked actions

- bind_public_network_interface
- return_raw_payload
- export_raw_memory_index
- send_external_message
- publish_external_content
- call_external_provider
- delete_retrieval_logs
- commit_raw_api_cache
- bypass_sanitization

## Next checkpoint

- 044 - K-Agent Context Injection Layer