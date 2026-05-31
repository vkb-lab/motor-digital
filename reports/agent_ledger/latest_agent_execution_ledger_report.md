# K-OS Agent Execution Ledger and Replay Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T20:32:33+00:00
- Ledger committed: False
- Replay dry-run default: True
- Replay execution requires approval: True
- Command Center available: True
- External publish enabled: False

## Metrics

- ledger_entry_count: 2
- replay_count: 2
- executed_entry_count: 0
- dry_run_entry_count: 2
- failed_entry_count: 0
- replay_dry_run_count: 2
- replay_executed_count: 0
- status_counts: {'dispatch_completed': 2}
- action_counts: {'cockpit_audit': 2}
- agent_counts: {'k_atlas_engineer': 2}

## Ledger entries

- led_41940b4ebda6 | k_atlas_engineer | cockpit_audit | status=dispatch_completed | dry_run=True | executed=False
- led_6c01e8eb39e2 | k_atlas_engineer | cockpit_audit | status=dispatch_completed | dry_run=True | executed=False

## Recent replays

- rpl_bb38b9f45743 | ledger=led_41940b4ebda6 | status=replay_completed | dry_run=True | executed=False
- rpl_d1fb62ffe6a9 | ledger=led_6c01e8eb39e2 | status=replay_completed | dry_run=True | executed=False

## Required gates before replay

- ledger_entry_exists
- action_exists_in_command_center
- input_hash_available
- output_hash_available
- dry_run_completed
- approval_present_if_execute
- operator_reason_present_if_execute
- audit_event_recorded

## Blocked actions

- replay_without_approval
- execute_replay_without_command_center
- delete_execution_ledger
- delete_replay_evidence
- commit_raw_ledger_data
- send_external_message
- publish_external_content
- call_external_provider
- modify_hashes
- bypass_approval_gate

## Next checkpoint

- 042 - K-Memory Event Bus and Context Index Core