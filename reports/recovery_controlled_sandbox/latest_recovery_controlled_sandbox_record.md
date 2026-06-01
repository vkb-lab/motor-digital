# K-OS Recovery Controlled Execution Sandbox Record

- Sandbox ID: rcs_ad461bff2e64
- Status: sandbox_blocked_by_governance
- Mode: safe_block
- Manual Stub status: intent_blocked
- Final Gate status: blocked
- Dry Run status: missing
- Recovery Gate status: blocked
- Recovery Plan ID: rpb_be687cf9460f
- Readiness level: review_required
- Risk level: medium
- Workspace hash: 4b71f3130180061dc08c83acc58e2ce5ff60e609c8973bb94b126dcf5f5e09d2
- Sandbox hash: 93ce9d2de8a42992f19be7f2fa8714c0ed65bf42d3a0144b81c2c1ca67cc61bd
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False
- Executes shell: False

## Sandbox steps

- 1 | load_sanitized_evidence_chain | simulated=True | destructive=False
- 2 | validate_gate_alignment | simulated=True | destructive=False
- 3 | prepare_local_only_workspace_manifest | simulated=True | destructive=False
- 4 | block_destructive_operations | simulated=True | destructive=False
- 5 | prepare_operator_review | simulated=True | destructive=False

## Blockers

- operator_blocked_recovery
- operator_final_gate_blocks_recovery
- operator_manual_stub_blocks_recovery
- readiness_not_controlled_ready
- recovery_dry_run_hash_missing
- recovery_dry_run_missing
- {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- {'checkpoint': '056', 'blocker': 'blocked_status_present'}