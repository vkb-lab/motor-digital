# K-OS Rollback Governance Summary

- Summary ID: rgs_8ded4eeda1f9
- Status: closed_safe
- Hash: e0076fed68d8adca818620e50e7b777cec0b4d2eefbeb34827a816abc2283c25
- Covered checkpoints: 053, 054, 055, 056, 057, 058, 059
- No real rollback executed: True
- No data deleted: True
- No target files modified: True
- No git reset executed: True
- No force push executed: True
- No shell execution: True

## Totals

- checkpoint_count: 7
- available_report_count: 7
- available_artifact_count: 7
- missing_report_count: 0
- missing_artifact_count: 0
- rollback_execution_count: 0
- data_delete_count: 0
- target_file_modify_count: 0
- file_modify_count: 0
- git_reset_count: 0
- git_force_push_count: 0
- shell_execution_count: 0
- raw_payload_count: 0

## Chain

- 053 | Rollback Preparation Core | report=True | artifact=True | status=audit_generated
- 054 | Rollback Approval and Release Gate Core | report=True | artifact=True | status=audit_generated
- 055 | Rollback Dry Run Simulator Core | report=True | artifact=True | status=audit_generated
- 056 | Rollback Execution Final Gate Core | report=True | artifact=True | status=audit_generated
- 057 | Rollback Manual Execution Stub Core | report=True | artifact=True | status=audit_generated
- 058 | Rollback Controlled Execution Sandbox Core | report=True | artifact=True | status=audit_generated
- 059 | Rollback Sandbox Report and Operator Review Core | report=True | artifact=True | status=audit_generated

## Consolidated blockers

- 053: blocked_status_present
- 054: blocked_status_present
- 056: blocked_status_present