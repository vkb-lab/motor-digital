# K-OS Recovery Governance Summary

- Summary ID: rgs2_ccd59093b101
- Status: closed_with_review_required
- Hash: 5b2d2076354fd942c389ddbf43279e0523662139ef95c7f98ae419ce4d75562a
- Covered checkpoints: 061, 062, 063, 064, 065, 066, 067, 068
- Evidence chain complete: False
- No recovery executed: True
- No rollback executed: True
- No data deleted: True
- No target files modified: True
- No git reset executed: True
- No force push executed: True
- No shell executed: True

## Totals

- checkpoint_count: 8
- available_report_count: 7
- available_artifact_count: 7
- missing_report_count: 1
- missing_artifact_count: 1
- destructive_flag_count: 0
- recovery_execution_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- raw_payload_count: 0

## Evidence chain

- 061 | Recovery Readiness Matrix Core | report=True | artifact=True | status=matrix_generated
- 062 | Recovery Plan Builder Core | report=True | artifact=True | status=plan_blocked_review_required
- 063 | Recovery Approval Gate Core | report=True | artifact=True | status=blocked
- 064 | Recovery Dry Run Simulator Core | report=False | artifact=False | status=missing
- 065 | Recovery Final Gate Core | report=True | artifact=True | status=blocked
- 066 | Recovery Manual Execution Stub Core | report=True | artifact=True | status=intent_blocked
- 067 | Recovery Controlled Execution Sandbox Core | report=True | artifact=True | status=sandbox_blocked_by_governance
- 068 | Recovery Sandbox Operator Review Core | report=True | artifact=True | status=review_acknowledged_blocked

## Consolidated blockers

- 062: readiness_not_controlled_ready
- 062: {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- 062: {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- 062: {'checkpoint': '056', 'blocker': 'blocked_status_present'}
- 063: operator_blocked_recovery
- 064: report_missing
- 064: artifact_missing
- 065: operator_blocked_recovery
- 065: readiness_not_controlled_ready
- 065: recovery_dry_run_hash_missing
- 065: recovery_dry_run_missing
- 065: {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- 065: {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- 065: {'checkpoint': '056', 'blocker': 'blocked_status_present'}
- 065: operator_final_gate_blocks_recovery
- 066: operator_blocked_recovery
- 066: operator_final_gate_blocks_recovery
- 066: readiness_not_controlled_ready
- 066: recovery_dry_run_hash_missing
- 066: recovery_dry_run_missing
- 066: {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- 066: {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- 066: {'checkpoint': '056', 'blocker': 'blocked_status_present'}
- 066: operator_manual_stub_blocks_recovery
- 067: operator_blocked_recovery
- 067: operator_final_gate_blocks_recovery
- 067: operator_manual_stub_blocks_recovery
- 067: readiness_not_controlled_ready
- 067: recovery_dry_run_hash_missing
- 067: recovery_dry_run_missing
- 067: {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- 067: {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- 067: {'checkpoint': '056', 'blocker': 'blocked_status_present'}