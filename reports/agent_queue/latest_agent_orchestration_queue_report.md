# K-OS Agent Orchestration Queue Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T20:19:12+00:00
- Queue committed: False
- Command Center available: True
- Permission Matrix available: True
- Dry-run default: True
- Dispatch via Command Center only: True

## Metrics

- task_count: 1
- dispatch_count: 1
- blocked_task_count: 0
- queued_task_count: 0
- approved_task_count: 0
- status_counts: {'dispatched_dry_run': 1}
- priority_counts: {'medium': 1}
- agent_counts: {'k_atlas_engineer': 1}

## Tasks

- agtq_57ac77ce7032 | k_atlas_engineer | cockpit_audit | priority=medium | status=dispatched_dry_run | approved=True

## Recent dispatches

- disp_e18dd12228c5 | task=agtq_57ac77ce7032 | status=dispatch_completed | dry_run=True | executed=False

## Required gates before dispatch

- task_exists
- agent_allowed
- action_exists_in_command_center
- risk_level_classified
- operator_reason_present
- approval_present_if_required
- audit_event_recorded

## Blocked actions

- dispatch_agent_without_permission
- execute_task_without_approval
- run_arbitrary_agent_command
- bypass_command_center
- send_external_message
- publish_external_content
- call_external_provider
- delete_queue_audit_logs
- commit_raw_queue_data

## Next checkpoint

- 040 - K-Agent Runtime Supervisor Core