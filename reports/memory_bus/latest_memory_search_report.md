# K-OS Memory Search Report

- Status: search_completed
- Query: agent
- Event matches: 42
- Context matches: 5
- Raw payload included: False
- External publish enabled: False

## Event matches

- 2026-05-31T20:32:33+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.execution_recorded
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
- 2026-05-31T20:32:32+00:00 | agent_ledger | agent_ledger | agent_ledger.replay_completed
- 2026-05-31T20:32:31+00:00 | agent_ledger | agent_ledger | agent_ledger.audit_generated
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

## Context matches

- governance | agent_permission_matrix | status=passed | path=reports/governance/latest_agent_permission_matrix_report.json
- command_center | command_center | status=audit_generated | path=reports/command_center/latest_command_center_action_router_report.json
- agent_queue | agent_queue | status=audit_generated | path=reports/agent_queue/latest_agent_orchestration_queue_report.json
- agent_runtime | agent_runtime | status=audit_generated | path=reports/agent_runtime/latest_agent_runtime_supervisor_report.json
- agent_ledger | agent_ledger | status=audit_generated | path=reports/agent_ledger/latest_agent_execution_ledger_report.json