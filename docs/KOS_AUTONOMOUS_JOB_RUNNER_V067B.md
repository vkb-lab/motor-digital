# K-OS Autonomous Job Runner v0.67B

Objetivo: executar o primeiro job autonomo local com seguranca.

Acoes permitidas:
- write_json_report

Acoes bloqueadas:
- shell_exec
- deploy
- paid_ai_call
- instagram_publish
- browser_logged_account_automation

O runner verifica o Autonomy Kill Switch antes de executar jobs.

Comando:
powershell:
python scripts\run_phase67b_autonomous_job_runner.py --limit 5
