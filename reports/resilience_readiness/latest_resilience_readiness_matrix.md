# K-OS Resilience Readiness Matrix

- Matrix ID: rrm_b829e2b45daf
- Status: resilience_blocked
- Score: 65/100
- Percent: 65.0
- Level: low
- Hash: c0a79c80d7c05e89116da9034e78172fd44ef6b019aa31d1226b95b0be62e30f
- Recovery layer closure: layer_blocked
- Destructive zero confirmed: True
- Executes recovery: False
- Executes rollback: False
- Executes shell: False

## Dimensions

- recovery_layer_closed | ok=False | score=0/20
- evidence_chain_complete | ok=False | score=0/15
- governance_summary_available | ok=True | score=15/15
- destructive_zero_confirmed | ok=True | score=20/20
- operator_review_available | ok=True | score=10/10
- local_state_isolated | ok=True | score=5/5
- security_firewall_available | ok=True | score=10/10
- next_layer_ready | ok=True | score=5/5

## Blockers

- recovery_layer_closure_missing_or_not_closed
- evidence_core_chain_incomplete