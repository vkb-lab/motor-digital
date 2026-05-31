# K-OS Context Retrieval Report

- Status: retrieval_completed
- Retrieval ID: ret_b7f9219562b7
- Query: agent
- Domain: 
- Module: 
- Events: 10
- Contexts: 5
- Raw payload included: False
- External publish enabled: False

## Events

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

## Context items

- governance | agent_permission_matrix | status=passed | path=reports/governance/latest_agent_permission_matrix_report.json
- command_center | command_center | status=audit_generated | path=reports/command_center/latest_command_center_action_router_report.json
- agent_queue | agent_queue | status=audit_generated | path=reports/agent_queue/latest_agent_orchestration_queue_report.json
- agent_runtime | agent_runtime | status=audit_generated | path=reports/agent_runtime/latest_agent_runtime_supervisor_report.json
- agent_ledger | agent_ledger | status=audit_generated | path=reports/agent_ledger/latest_agent_execution_ledger_report.json