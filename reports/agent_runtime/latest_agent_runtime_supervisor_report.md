# K-OS Agent Runtime Supervisor Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T20:25:40+00:00
- Watchdog health: healthy
- Runtime state committed: False
- Permission Matrix available: True
- Command Center available: True
- Agent Queue report available: True
- External publish enabled: False

## Metrics

- agent_count: 1
- healthy_agent_count: 1
- attention_agent_count: 0
- blocked_agent_count: 0
- stale_agent_count: 0
- queue_task_count: 1
- queue_blocked_task_count: 0
- queue_dispatch_count: 1
- status_counts: {'idle': 1}
- health_counts: {'healthy': 1}

## Agents

- k_atlas_engineer | status=idle | health=healthy | heartbeat_age=0.01

## Watchdog blockers

- Nenhum blocker.

## Required gates before runtime execution

- agent_registered
- agent_allowed
- heartbeat_recent
- queue_task_valid
- permission_matrix_available
- command_center_available
- operator_approval_if_required
- audit_event_recorded

## Blocked actions

- execute_agent_without_runtime_registration
- execute_agent_without_heartbeat
- continue_stale_agent
- bypass_agent_queue
- bypass_command_center
- delete_runtime_audit_logs
- commit_raw_runtime_state
- send_external_message
- publish_external_content
- call_external_provider

## Next checkpoint

- 041 - K-Agent Execution Ledger and Replay Core