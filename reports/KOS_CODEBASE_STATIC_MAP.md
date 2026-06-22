# K-OS Codebase Static Map

Status: mapa estático criado sem IA, sem instalação externa e sem API.

## Totais
- python_files: 3334
- files_with_risk_hits: 779
- files_with_streamlit_hits: 218
- functions_total: 8468
- classes_total: 1139

## Arquivos de maior interesse
### pages/85_K_Atlas_Local_Action_Router.py
- score: 7
- linhas: 39
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/938_K_OS_Command_Center_Action_Router.py
- score: 7
- linhas: 156
- funções: python_exe, read_json, run
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/948_K_OS_Agent_Safe_Execution_Router_Core.py
- score: 7
- linhas: 143
- funções: python_exe, read_json, run
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/975_K_OS_Agent_Resilience_Drill_Operator_Review_Core.py
- score: 7
- linhas: 128
- funções: python_exe, read_json, run
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/KOS_Operator_Chat.py
- score: 7
- linhas: 479
- funções: list_safe_actions, read_json, render_hupmix_gp_lousa_preview, run_action_router, run_safe_action, show_operator_response, show_safe_action_history, show_safe_action_result, subprocess_env
- classes: -
- riscos: subprocess, publish
- streamlit: st.button, st.text_area, st.video

### _local_quarantine/untracked_20260604_122743/.codex_phase5/.tmp/plugins/plugins/nvidia/skills/dynamo-router-starter/scripts/check_router_health.py
- score: 5
- linhas: 143
- funções: choose_model, main, request_json
- classes: -
- riscos: urllib
- streamlit: -

### pages/09_K_Atlas_Control_Plane.py
- score: 5
- linhas: 316
- funções: load_execution_records, load_json, load_jsonl
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/121_K_Atlas_Operator_Clipboard_Return.py
- score: 5
- linhas: 23
- funções: -
- classes: -
- riscos: -
- streamlit: st.button, st.text_area

### pages/12_K_Atlas_Social_Audit_Local.py
- score: 5
- linhas: 184
- funções: list_report_dirs, load_json_list
- classes: -
- riscos: openai
- streamlit: st.button

### pages/133_K_Atlas_Local_OS_Brain_Governance.py
- score: 5
- linhas: 86
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/17_K_Atlas_Sandbox_API_Adapter.py
- score: 5
- linhas: 102
- funções: -
- classes: -
- riscos: requests., publish
- streamlit: st.button, st.text_area

### pages/20_K_Atlas_Deploy_Pipeline.py
- score: 5
- linhas: 91
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/21_K_Atlas_Assisted_Autonomy.py
- score: 5
- linhas: 96
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/26_K_Atlas_Mission_Executor_Bridge.py
- score: 5
- linhas: 91
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/29_K_Atlas_Daily_Operator_Cockpit.py
- score: 5
- linhas: 84
- funções: -
- classes: -
- riscos: -
- streamlit: st.button

### pages/31_K_Atlas_AI_Provider_Router.py
- score: 5
- linhas: 88
- funções: -
- classes: -
- riscos: -
- streamlit: st.button, st.text_area

### pages/33_K_Atlas_Instagram_Graph_Readiness.py
- score: 5
- linhas: 99
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/35_K_Atlas_Secure_Publish_Approval_Gate.py
- score: 5
- linhas: 110
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/36_K_Atlas_External_Action_Stub.py
- score: 5
- linhas: 79
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/38_K_Atlas_Adapter_Dry_Run_Orchestrator.py
- score: 5
- linhas: 97
- funções: -
- classes: -
- riscos: openai, publish
- streamlit: st.button

### pages/39_K_Atlas_Service_Readiness_Matrix.py
- score: 5
- linhas: 115
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/40_K_Atlas_Operator_Mission_Queue.py
- score: 5
- linhas: 104
- funções: -
- classes: -
- riscos: -
- streamlit: st.button, st.text_area

### pages/42_K_Atlas_Command_Center_Planning_Runner.py
- score: 5
- linhas: 96
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/43_K_Atlas_Planning_Approval_Packager.py
- score: 5
- linhas: 100
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/64_Decision_Flow_Router.py
- score: 5
- linhas: 70
- funções: -
- classes: -
- riscos: -
- streamlit: st.button

### pages/65_K_Atlas_Assisted_Autoprogramming.py
- score: 5
- linhas: 106
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/67_K_Atlas_Autoprogramming_Apply_Package_Builder.py
- score: 5
- linhas: 69
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/69_K_Atlas_Manual_Apply_Executor.py
- score: 5
- linhas: 52
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py
- score: 5
- linhas: 52
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/72_K_Atlas_Autoprogramming_Cycle_Controller.py
- score: 5
- linhas: 38
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/73_K_Atlas_Local_Mission_Installer.py
- score: 5
- linhas: 102
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/76_K_Atlas_Mission_Pipeline_Runner.py
- score: 5
- linhas: 83
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button

### pages/80_K_Atlas_Operator_Approval_Console.py
- score: 5
- linhas: 45
- funções: -
- classes: -
- riscos: -
- streamlit: st.button, st.text_area

### pages/902_K_Uni_Marketplace_IA_Instagram_Approval_Gate.py
- score: 5
- linhas: 79
- funções: -
- classes: -
- riscos: publish
- streamlit: st.button, st.text_area

### pages/913_K_Uni_Git_Bridge.py
- score: 5
- linhas: 175
- funções: ensure_git_bridge, render_result, run_git, safe_add
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/914_K_OS_GitHub_Admin_API_Bridge.py
- score: 5
- linhas: 85
- funções: run_action
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/915_K_OS_Security_Firewall.py
- score: 5
- linhas: 113
- funções: python_exe, run_mode
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/916_K_OS_Schema_Guard.py
- score: 5
- linhas: 123
- funções: python_exe, run
- classes: -
- riscos: subprocess
- streamlit: st.button

### pages/917_K_OS_Agent_Permission_Matrix.py
- score: 5
- linhas: 111
- funções: python_exe, run_validate
- classes: -
- riscos: subprocess, publish
- streamlit: st.button

### pages/918_K_OS_Vault_Guard.py
- score: 5
- linhas: 114
- funções: run_action
- classes: -
- riscos: subprocess, openai
- streamlit: st.button

## Decisão
Codebase Memory MCP permanece pausado. Este scanner interno entrega o primeiro mapa técnico sem risco operacional.