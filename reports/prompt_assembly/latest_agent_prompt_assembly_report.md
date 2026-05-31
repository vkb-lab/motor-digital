# K-OS Agent Prompt Assembly and Execution Plan Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T21:16:40+00:00
- State committed: False
- Raw payload prompt allowed: False
- Secret in prompt allowed: False
- Dry-run default: True
- External publish enabled: False

## Metrics

- prompt_package_count: 2
- validation_count: 1
- assembled_count: 0
- validated_count: 0
- blocked_count: 2
- raw_payload_package_count: 0
- secret_package_count: 0
- status_counts: {'blocked': 2}
- agent_counts: {'k_atlas_engineer': 2}

## Recent prompt packages

- prmpt_85de1293d01a | agent=k_atlas_engineer | task=closure_prompt_assembly_validation | status=blocked | action=cockpit_audit
- prmpt_00c0daca2d42 | agent=k_atlas_engineer | task=manual_prompt_task | status=blocked | action=cockpit_audit

## Required gates before agent execution

- context_packet_exists
- context_packet_validated
- prompt_assembled
- execution_plan_created
- raw_payload_removed
- secret_scan_passed
- dry_run_completed
- operator_approval_if_real_execution
- audit_event_recorded

## Blocked actions

- assemble_prompt_with_raw_payload
- assemble_prompt_with_secret
- execute_without_plan
- execute_without_approval
- bypass_command_center
- send_external_message
- publish_external_content
- call_external_provider
- commit_raw_prompt_state
- delete_prompt_audit_logs

## Next checkpoint

- 046 - K-Agent Dry Run Executor Core