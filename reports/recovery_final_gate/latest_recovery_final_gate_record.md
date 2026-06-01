# K-OS Recovery Final Gate Record

- Recovery Final Gate ID: rfg_c42bd422642f
- Status: blocked
- Mode: block_execution
- Recovery Dry Run ID: 
- Recovery Dry Run status: missing
- Recovery Gate status: blocked
- Recovery Plan ID: rpb_be687cf9460f
- Readiness level: review_required
- Risk level: medium
- Final gate hash: ad387ef8169245a22536f2f769dd4b3fc8ac24cfb2d207693cdc1a7fd0d0d942
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell: False

## Blockers

- operator_blocked_recovery
- readiness_not_controlled_ready
- recovery_dry_run_hash_missing
- recovery_dry_run_missing
- {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- {'checkpoint': '056', 'blocker': 'blocked_status_present'}
- operator_final_gate_blocks_recovery