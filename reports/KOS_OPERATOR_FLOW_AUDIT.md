# K-OS Operator Flow Audit

Status: auditoria do fluxo operador criada sem IA e sem ferramentas externas.

## Resumo
- candidate_python_files: 2946
- interesting_python_files: 880
- core_files: 851
- skipped_empty_or_unreadable: 21
- files_with_subprocess_or_browser: 140
- files_with_ui_lines: 216
- files_with_runtime_or_reports: 427

## Arquivos centrais
### pages/KOS_Operator_Chat.py
- score: 22
- linhas: 479
- funcoes: list_safe_actions, read_json, render_hupmix_gp_lousa_preview, run_action_router, run_safe_action, show_operator_response, show_safe_action_history, show_safe_action_result, subprocess_env
- riscos: publish, subprocess
- ui_hits: 22
- subprocess/browser hits: 8
- runtime/report hits: 26

### scripts/run_phase72g_safe_action_executor.py
- score: 14
- linhas: 972
- funcoes: as_lines, build_admin, build_agents, build_general, build_hupmix_gp_continuity, build_hupmix_gp_video_01_production_kit, build_patches, build_runtime, build_saas, build_social, build_social_read, clip, compact_value, execute_safe_action, extract_signals, fallback, kos_is_social_read_request, main, mtime_label, now_iso, read_json, render_markdown, safe_number, summarize_decision_queue, summarize_json_file
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 20

### scripts/run_kos_operator_flow_audit.py
- score: 12
- linhas: 313
- funcoes: -
- riscos: subprocess, os.system, webbrowser, requests., urllib, openai, google.generativeai, anthropic, publish, upload, delete, ACCESS_TOKEN, META_ACCESS_TOKEN
- ui_hits: 7
- subprocess/browser hits: 10
- runtime/report hits: 17

### pages/938_K_OS_Command_Center_Action_Router.py
- score: 12
- linhas: 156
- funcoes: python_exe, read_json, run
- riscos: subprocess
- ui_hits: 4
- subprocess/browser hits: 2
- runtime/report hits: 5

### pages/948_K_OS_Agent_Safe_Execution_Router_Core.py
- score: 12
- linhas: 143
- funcoes: python_exe, read_json, run
- riscos: subprocess
- ui_hits: 4
- subprocess/browser hits: 2
- runtime/report hits: 3

### pages/975_K_OS_Agent_Resilience_Drill_Operator_Review_Core.py
- score: 12
- linhas: 128
- funcoes: python_exe, read_json, run
- riscos: subprocess
- ui_hits: 3
- subprocess/browser hits: 2
- runtime/report hits: 3

### scripts/kos_phase38_install_safe_executor.py
- score: 11
- linhas: 356
- funcoes: now, save_json, write
- riscos: delete, openai, publish, subprocess
- ui_hits: 1
- subprocess/browser hits: 2
- runtime/report hits: 11

### pages/949_K_OS_Agent_Allowlisted_Action_Executor_Core.py
- score: 11
- linhas: 142
- funcoes: python_exe, read_json, run
- riscos: subprocess
- ui_hits: 4
- subprocess/browser hits: 2
- runtime/report hits: 3

### pages/946_K_OS_Agent_Dry_Run_Executor_Core.py
- score: 11
- linhas: 128
- funcoes: python_exe, read_json, run
- riscos: subprocess
- ui_hits: 4
- subprocess/browser hits: 2
- runtime/report hits: 3

### ops/k_os_command_center_action_router.py
- score: 10
- linhas: 610
- funcoes: action_requires_approval, audit_report, ensure_state, event, load_policy, main, now, read_json, record_execution, resolve_command, route_action, safe_catalog, save_state, show_latest, write_catalog, write_execution, write_json, write_report
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 13

### scripts/run_phase72f_orchestrator_action_router.py
- score: 10
- linhas: 392
- funcoes: build_packet, call_72c, detect_route, is_social_read_request, main, normalize, normalize_social_intent_text, now_iso, save_packet, summarize_request
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 13

### scripts/kos_phase46_install_operator_briefing.py
- score: 10
- linhas: 387
- funcoes: now, save_json, write
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 2

### k_atlas/core/daily_operator/cockpit.py
- score: 10
- linhas: 233
- funcoes: __init__, check_url, collect, read_json, run_git, save_report, to_markdown, utc_now
- riscos: subprocess, urllib
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 11

### k_atlas/kaizen/operator_briefing.py
- score: 10
- linhas: 226
- funcoes: _call_summary, _run, _save_json, build_operator_briefing, get_git_summary, now, render_markdown
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 1

### k_atlas/ai/provider_router_v2.py
- score: 10
- linhas: 126
- funcoes: _run_ollama, run_ai
- riscos: subprocess, urllib
- ui_hits: 0
- subprocess/browser hits: 1
- runtime/report hits: 0

### k_atlas/kaizen/queue_approval_executor.py
- score: 9
- linhas: 387
- funcoes: command_key_for, ensure_dirs, execute_one_approval, execution_marker_paths, file_hash, find_staged_json, list_staged_jsons, main, move_approval, normalize_bool, now_iso, process_approvals, read_json, resolve_under_root, safe_read_approval_json, validate_approval, validate_staged, write_event, write_json
- riscos: publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 1

### k_atlas/kaizen/safe_executor.py
- score: 9
- linhas: 206
- funcoes: _command_has_blocked_keyword, _read_json, _save_json, is_allowed_action, list_safe_actions, now, run_action, run_phase38_smoke, run_safe_bundle
- riscos: openai, publish, subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 4

### k_atlas/live/auto_executor.py
- score: 9
- linhas: 71
- funcoes: -
- riscos: subprocess
- ui_hits: 0
- subprocess/browser hits: 2
- runtime/report hits: 0

### pages/85_K_Atlas_Local_Action_Router.py
- score: 9
- linhas: 39
- funcoes: -
- riscos: publish
- ui_hits: 1
- subprocess/browser hits: 0
- runtime/report hits: 1

### pages/26_K_Atlas_Mission_Executor_Bridge.py
- score: 8
- linhas: 91
- funcoes: -
- riscos: publish
- ui_hits: 2
- subprocess/browser hits: 0
- runtime/report hits: 2

### pages/69_K_Atlas_Manual_Apply_Executor.py
- score: 8
- linhas: 52
- funcoes: -
- riscos: publish
- ui_hits: 3
- subprocess/browser hits: 0
- runtime/report hits: 0

### pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py
- score: 8
- linhas: 52
- funcoes: -
- riscos: publish
- ui_hits: 2
- subprocess/browser hits: 0
- runtime/report hits: 0

### agents/decision_flow_router.py
- score: 7
- linhas: 848
- funcoes: -
- riscos: publish
- ui_hits: 0
- subprocess/browser hits: 0
- runtime/report hits: 8

### ops/k_os_agent_resilience_drill_operator_review_core.py
- score: 7
- linhas: 721
- funcoes: audit_report, create_review, detect_destructive_flags, ensure_state, event, latest_review_raw, load_policy, main, now, read_json, rel, review_dimension, safe_review, save_state, show_latest, source_ref, stable_hash, validate_latest, write_json, write_report, write_review, write_validation
- riscos: delete, publish
- ui_hits: 0
- subprocess/browser hits: 0
- runtime/report hits: 8

### ops/k_os_agent_safe_execution_router_core.py
- score: 7
- linhas: 679
- funcoes: audit_report, compute_metrics, create_route, ensure_state, event, latest_approval_from_local_state, latest_route_raw, load_approval_decision, load_approval_validation, load_dry_run_result, load_policy, main, now, permission_summary, pick_route_target, read_json, route_gate_check, safe_route_for_report, save_state, show_latest, stable_hash, validate_latest, write_json, write_report, write_route
- riscos: publish
- ui_hits: 0
- subprocess/browser hits: 0
- runtime/report hits: 10

### k_atlas/kos_base/workspace.py
- score: 7
- linhas: 573
- funcoes: add_board_card, build_client_rows, build_connector_rows, build_report_rows, build_workspace_snapshot, ensure_base_board, inject_base_css, load_audit_events, load_publish_queue, move_card, read_json, read_runtime_presence, render_board, render_kos_base_workspace_panel, render_status_pill, run_git, utc_now
- riscos: publish, subprocess
- ui_hits: 5
- subprocess/browser hits: 2
- runtime/report hits: 11

### k_atlas/core/operator_mission_queue/queue.py
- score: 7
- linhas: 440
- funcoes: __init__, approve, build_tasks, default_payload, enqueue, event, export_command_center_tasks, list_by_status, load_queue, save_queue, save_report, summary, to_markdown, utc_now
- riscos: publish
- ui_hits: 0
- subprocess/browser hits: 0
- runtime/report hits: 5

### scripts/kos_phase48_install_evidence_ledger.py
- score: 7
- linhas: 377
- funcoes: now, save_json, write
- riscos: publish, subprocess
- ui_hits: 1
- subprocess/browser hits: 2
- runtime/report hits: 2

### k_atlas/core/ai_provider_router/router.py
- score: 7
- linhas: 341
- funcoes: __init__, build_matrix, default_payload, env_status, event, load_external_readiness, provider_ready, route, route_table, save_report, to_markdown, utc_now
- riscos: openai, publish
- ui_hits: 0
- subprocess/browser hits: 0
- runtime/report hits: 9

### pages/KOS_Unified_Command_Cockpit.py
- score: 7
- linhas: 220
- funcoes: -
- riscos: subprocess, publish
- ui_hits: 1
- subprocess/browser hits: 2
- runtime/report hits: 3

## Decisao
Proximo passo recomendado: criar painel de diagnostico do fluxo no Operator Chat.
Ainda nao instalar Codebase Memory MCP, IA paga ou geradores de video.