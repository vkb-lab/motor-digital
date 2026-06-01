# K-OS Resilience Drill Design

- Design ID: rddp_2908fe56d7d5
- Status: drills_designed
- Drill count: 8
- Hash: 71f7332d7887157792c55c07ef87cc986d4b15a9d9ebe3eb648989aaa6db6bfe
- Scenario plan status: scenarios_review_required
- Readiness status: resilience_blocked
- Executes drill: False
- Executes recovery: False
- Executes rollback: False
- Executes shell: False

## Drills

- rdd_909e608bfe | agent_runtime_failure | type=tabletop | severity=high
- rdd_bb00185594 | memory_integrity_risk | type=tabletop | severity=high
- rdd_ff68502dbf | security_firewall_block | type=tabletop | severity=high
- rdd_0f2cb49918 | dashboard_unavailable | type=audit_walkthrough | severity=medium
- rdd_5fd9b2ffb1 | external_api_unavailable | type=audit_walkthrough | severity=medium
- rdd_47ef53cea9 | git_sync_conflict | type=audit_walkthrough | severity=medium
- rdd_4e8f1420af | operator_misconfiguration | type=audit_walkthrough | severity=low
- rdd_d5a7ef9958 | report_generation_failure | type=audit_walkthrough | severity=low

## Blockers

- Nenhum blocker.