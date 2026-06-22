# K-OS Codebase Static Map Digest

Status: resumo compacto criado a partir do mapa estatico.

## Totais
- python_files: 3334
- files_with_risk_hits: 779
- files_with_streamlit_hits: 218
- functions_total: 8468
- classes_total: 1139

## Top riscos
- publish: 557
- subprocess: 175
- requests.: 67
- delete: 44
- urllib: 43
- openai: 35
- ACCESS_TOKEN: 20
- upload: 17
- META_ACCESS_TOKEN: 11
- Remove-Item: 7
- playwright: 5
- google.generativeai: 5
- os.system: 5
- webbrowser: 3
- anthropic: 3
- selenium: 2

## Categorias críticas

### operator_ui
- pages/KOS_Operator_Chat.py | linhas: 479 | riscos: subprocess, publish | streamlit: st.button, st.text_area, st.video
- ops/k_os_agent_resilience_drill_operator_review_core.py | linhas: 721 | riscos: publish, delete | streamlit: -
- scripts/kos_phase46_install_operator_briefing.py | linhas: 387 | riscos: subprocess, publish | streamlit: -
- k_atlas/core/daily_operator/cockpit.py | linhas: 233 | riscos: subprocess, urllib | streamlit: -
- k_atlas/kaizen/operator_briefing.py | linhas: 226 | riscos: subprocess, publish | streamlit: -
- pages/975_K_OS_Agent_Resilience_Drill_Operator_Review_Core.py | linhas: 128 | riscos: subprocess | streamlit: st.button
- pages/40_K_Atlas_Operator_Mission_Queue.py | linhas: 104 | riscos: - | streamlit: st.button, st.text_area
- pages/80_K_Atlas_Operator_Approval_Console.py | linhas: 45 | riscos: - | streamlit: st.button, st.text_area
- pages/121_K_Atlas_Operator_Clipboard_Return.py | linhas: 23 | riscos: - | streamlit: st.button, st.text_area
- k_atlas/core/operator_mission_queue/queue.py | linhas: 440 | riscos: publish | streamlit: -
- scripts/run_phase72a_weekly_operator_workspace.py | linhas: 142 | riscos: publish | streamlit: -
- k_atlas/core/operator_mission_queue/policy.py | linhas: 90 | riscos: publish | streamlit: -

### safe_action_executor
- scripts/kos_phase38_install_safe_executor.py | linhas: 356 | riscos: subprocess, openai, publish, delete | streamlit: st.button
- scripts/run_phase69h_hupmix_real_publish_executor.py | linhas: 389 | riscos: urllib, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- k_atlas/kaizen/safe_executor.py | linhas: 206 | riscos: subprocess, openai, publish | streamlit: -
- pages/26_K_Atlas_Mission_Executor_Bridge.py | linhas: 91 | riscos: publish | streamlit: st.button, st.text_area
- pages/69_K_Atlas_Manual_Apply_Executor.py | linhas: 52 | riscos: publish | streamlit: st.button, st.text_area
- scripts/run_phase72g_safe_action_executor.py | linhas: 972 | riscos: subprocess, publish | streamlit: -
- ops/k_os_agent_allowlisted_action_executor_core.py | linhas: 762 | riscos: publish, delete | streamlit: -
- k_atlas/kaizen/queue_approval_executor.py | linhas: 387 | riscos: subprocess, publish | streamlit: -
- k_atlas/core/manual_apply_rollback_executor/rollback.py | linhas: 307 | riscos: publish, delete | streamlit: -
- pages/949_K_OS_Agent_Allowlisted_Action_Executor_Core.py | linhas: 142 | riscos: subprocess | streamlit: st.button
- pages/946_K_OS_Agent_Dry_Run_Executor_Core.py | linhas: 128 | riscos: subprocess | streamlit: st.button
- k_atlas/core/manual_apply_rollback_executor/smoke_test_manual_apply_rollback_executor.py | linhas: 102 | riscos: publish, delete | streamlit: -

### router
- ops/k_os_command_center_action_router.py | linhas: 610 | riscos: subprocess, publish | streamlit: -
- scripts/run_phase72f_orchestrator_action_router.py | linhas: 392 | riscos: subprocess, publish | streamlit: -
- k_atlas/core/ai_provider_router/router.py | linhas: 341 | riscos: openai, publish | streamlit: -
- pages/938_K_OS_Command_Center_Action_Router.py | linhas: 156 | riscos: subprocess | streamlit: st.button
- pages/948_K_OS_Agent_Safe_Execution_Router_Core.py | linhas: 143 | riscos: subprocess | streamlit: st.button
- k_atlas/ai/provider_router_v2.py | linhas: 126 | riscos: subprocess, urllib | streamlit: -
- pages/31_K_Atlas_AI_Provider_Router.py | linhas: 88 | riscos: - | streamlit: st.button, st.text_area
- k_atlas/core/ai_provider_router/policy.py | linhas: 72 | riscos: openai, publish | streamlit: -
- pages/85_K_Atlas_Local_Action_Router.py | linhas: 39 | riscos: publish | streamlit: st.button
- agents/decision_flow_router.py | linhas: 848 | riscos: publish | streamlit: -
- ops/k_os_agent_safe_execution_router_core.py | linhas: 679 | riscos: publish | streamlit: -
- _local_quarantine/untracked_20260604_122743/.codex_phase5/.tmp/plugins/plugins/nvidia/skills/dynamo-router-starter/scripts/check_router_health.py | linhas: 143 | riscos: urllib | streamlit: -

### subprocess_shell
- scripts/run_kos_codebase_static_map.py | linhas: 192 | riscos: subprocess, os.system, webbrowser, requests., urllib, selenium, playwright, openai, google.generativeai, anthropic, META_ACCESS_TOKEN, ACCESS_TOKEN, publish, upload, delete, Remove-Item | streamlit: st.button, st.form_submit_button, st.text_area, st.chat_input, st.video, st.components, components.html
- scripts/kos_phase29_ai_trace_free_tools.py | linhas: 651 | riscos: subprocess, urllib, openai, google.generativeai, anthropic, ACCESS_TOKEN | streamlit: -
- k_atlas/kos_base/workspace.py | linhas: 573 | riscos: subprocess, publish | streamlit: st.button, st.form_submit_button, st.text_area
- pages/KOS_Operator_Chat.py | linhas: 479 | riscos: subprocess, publish | streamlit: st.button, st.text_area, st.video
- scripts/kos_phase38_install_safe_executor.py | linhas: 356 | riscos: subprocess, openai, publish, delete | streamlit: st.button
- pages/922_K_OS_External_API_Sandbox.py | linhas: 118 | riscos: subprocess, openai, publish | streamlit: st.button, st.text_area
- scripts/kos_phase36_install_planner_bridge.py | linhas: 344 | riscos: subprocess, urllib, openai, publish | streamlit: -
- agent_core.py | linhas: 204 | riscos: subprocess, webbrowser, selenium, google.generativeai | streamlit: -
- local_dashboard.py | linhas: 197 | riscos: subprocess | streamlit: st.button, st.form_submit_button, st.text_area
- k_atlas/self_evolution/risk_analyzer.py | linhas: 86 | riscos: subprocess, requests., delete, Remove-Item | streamlit: -
- _local_quarantine/untracked_20260604_122743/.codex_phase5/.tmp/plugins/plugins/life-science-research/skills/locus-to-gene-mapper-skill/scripts/map_locus_to_gene.py | linhas: 2210 | riscos: subprocess, requests., delete | streamlit: -
- _local_quarantine/untracked_20260604_122743/.codex_phase5/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/content_agent_client.py | linhas: 1830 | riscos: subprocess, urllib, upload | streamlit: -

### browser_or_automation
- scripts/run_kos_codebase_static_map.py | linhas: 192 | riscos: subprocess, os.system, webbrowser, requests., urllib, selenium, playwright, openai, google.generativeai, anthropic, META_ACCESS_TOKEN, ACCESS_TOKEN, publish, upload, delete, Remove-Item | streamlit: st.button, st.form_submit_button, st.text_area, st.chat_input, st.video, st.components, components.html
- agent_core.py | linhas: 204 | riscos: subprocess, webbrowser, selenium, google.generativeai | streamlit: -
- _local_quarantine/untracked_20260604_122743/.codex_phase5/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/export_report.py | linhas: 96 | riscos: subprocess, playwright | streamlit: -
- k_atlas/social/social_audit/profile_audit.py | linhas: 217 | riscos: playwright | streamlit: -
- k_atlas/core/desktop_actions.py | linhas: 67 | riscos: webbrowser | streamlit: -
- k_atlas/services/browser_operator.py | linhas: 66 | riscos: playwright | streamlit: -
- k_atlas/agents/publisher_instagram.py | linhas: 65 | riscos: playwright | streamlit: -

### external_api_or_llm
- scripts/run_kos_codebase_static_map.py | linhas: 192 | riscos: subprocess, os.system, webbrowser, requests., urllib, selenium, playwright, openai, google.generativeai, anthropic, META_ACCESS_TOKEN, ACCESS_TOKEN, publish, upload, delete, Remove-Item | streamlit: st.button, st.form_submit_button, st.text_area, st.chat_input, st.video, st.components, components.html
- scripts/kos_phase29_ai_trace_free_tools.py | linhas: 651 | riscos: subprocess, urllib, openai, google.generativeai, anthropic, ACCESS_TOKEN | streamlit: -
- scripts/kos_phase38_install_safe_executor.py | linhas: 356 | riscos: subprocess, openai, publish, delete | streamlit: st.button
- pages/922_K_OS_External_API_Sandbox.py | linhas: 118 | riscos: subprocess, openai, publish | streamlit: st.button, st.text_area
- scripts/run_phase69h_hupmix_real_publish_executor.py | linhas: 389 | riscos: urllib, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- _local_quarantine/untracked_20260604_122743/scripts/kos_phase28_ai_cost_audit.py | linhas: 369 | riscos: openai, google.generativeai, ACCESS_TOKEN, publish | streamlit: -
- scripts/kos_phase36_install_planner_bridge.py | linhas: 344 | riscos: subprocess, urllib, openai, publish | streamlit: -
- k_atlas/core/live_adapter_contract_registry/registry.py | linhas: 280 | riscos: openai, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- k_atlas/core/external_api_adapter/readiness.py | linhas: 260 | riscos: openai, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- agent_core.py | linhas: 204 | riscos: subprocess, webbrowser, selenium, google.generativeai | streamlit: -
- scripts/run_phase69d_hupmix_instagram_audit.py | linhas: 202 | riscos: urllib, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- scripts/run_kos_meta_app_diagnostic.py | linhas: 184 | riscos: urllib, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -

### publish_upload_delete
- scripts/run_kos_codebase_static_map.py | linhas: 192 | riscos: subprocess, os.system, webbrowser, requests., urllib, selenium, playwright, openai, google.generativeai, anthropic, META_ACCESS_TOKEN, ACCESS_TOKEN, publish, upload, delete, Remove-Item | streamlit: st.button, st.form_submit_button, st.text_area, st.chat_input, st.video, st.components, components.html
- k_atlas/kos_base/workspace.py | linhas: 573 | riscos: subprocess, publish | streamlit: st.button, st.form_submit_button, st.text_area
- pages/KOS_Operator_Chat.py | linhas: 479 | riscos: subprocess, publish | streamlit: st.button, st.text_area, st.video
- scripts/kos_phase38_install_safe_executor.py | linhas: 356 | riscos: subprocess, openai, publish, delete | streamlit: st.button
- pages/922_K_OS_External_API_Sandbox.py | linhas: 118 | riscos: subprocess, openai, publish | streamlit: st.button, st.text_area
- _local_quarantine/untracked_20260604_122743/KOS_PHASE7_REPAIR.py | linhas: 591 | riscos: META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: st.button
- scripts/run_phase69h_hupmix_real_publish_executor.py | linhas: 389 | riscos: urllib, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- _local_quarantine/untracked_20260604_122743/scripts/kos_phase28_ai_cost_audit.py | linhas: 369 | riscos: openai, google.generativeai, ACCESS_TOKEN, publish | streamlit: -
- scripts/kos_phase36_install_planner_bridge.py | linhas: 344 | riscos: subprocess, urllib, openai, publish | streamlit: -
- k_atlas/saas_factory/products/brics-paraguay-autos/app.py | linhas: 334 | riscos: upload | streamlit: st.button, st.form_submit_button, st.text_area
- k_atlas/core/live_adapter_contract_registry/registry.py | linhas: 280 | riscos: openai, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -
- k_atlas/core/external_api_adapter/readiness.py | linhas: 260 | riscos: openai, META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: -

### streamlit_interaction
- scripts/run_kos_codebase_static_map.py | linhas: 192 | riscos: subprocess, os.system, webbrowser, requests., urllib, selenium, playwright, openai, google.generativeai, anthropic, META_ACCESS_TOKEN, ACCESS_TOKEN, publish, upload, delete, Remove-Item | streamlit: st.button, st.form_submit_button, st.text_area, st.chat_input, st.video, st.components, components.html
- k_atlas/kos_base/workspace.py | linhas: 573 | riscos: subprocess, publish | streamlit: st.button, st.form_submit_button, st.text_area
- pages/KOS_Operator_Chat.py | linhas: 479 | riscos: subprocess, publish | streamlit: st.button, st.text_area, st.video
- scripts/kos_phase38_install_safe_executor.py | linhas: 356 | riscos: subprocess, openai, publish, delete | streamlit: st.button
- pages/922_K_OS_External_API_Sandbox.py | linhas: 118 | riscos: subprocess, openai, publish | streamlit: st.button, st.text_area
- _local_quarantine/untracked_20260604_122743/KOS_PHASE7_REPAIR.py | linhas: 591 | riscos: META_ACCESS_TOKEN, ACCESS_TOKEN, publish | streamlit: st.button
- k_atlas/saas_factory/products/brics-paraguay-autos/app.py | linhas: 334 | riscos: upload | streamlit: st.button, st.form_submit_button, st.text_area
- local_dashboard.py | linhas: 197 | riscos: subprocess | streamlit: st.button, st.form_submit_button, st.text_area
- pages/17_K_Atlas_Sandbox_API_Adapter.py | linhas: 102 | riscos: requests., publish | streamlit: st.button, st.text_area
- scripts/kos_phase39_install_human_approval.py | linhas: 486 | riscos: publish | streamlit: st.button, st.text_area
- scripts/kos_phase37_install_mission_queue.py | linhas: 431 | riscos: publish | streamlit: st.button, st.text_area
- k_atlas/social/ui/social_cockpit_view.py | linhas: 389 | riscos: publish | streamlit: st.form_submit_button, st.text_area

## Recomendacao
Proximo passo: auditar o fluxo Operator Chat -> Router -> Safe Action Executor.
Nao conectar Codebase Memory MCP, IA paga ou ferramentas externas ainda.