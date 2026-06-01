# K-OS Recovery Manual Execution Stub Record

- Recovery Manual Stub ID: rms_e5c9c9c0fc5a
- Status: intent_blocked
- Mode: record_blocked_intent
- Recovery Final Gate status: blocked
- Recovery Dry Run status: missing
- Recovery Gate status: blocked
- Recovery Plan ID: rpb_be687cf9460f
- Readiness level: review_required
- Risk level: medium
- Stub hash: dfab2632158392649e8f44199bfb5fdc45f734c32ea3ab79aae45de5b583c392
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell: False

## Blockers

- operator_blocked_recovery
- operator_final_gate_blocks_recovery
- readiness_not_controlled_ready
- recovery_dry_run_hash_missing
- recovery_dry_run_missing
- {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- {'checkpoint': '056', 'blocker': 'blocked_status_present'}
- operator_manual_stub_blocks_recovery