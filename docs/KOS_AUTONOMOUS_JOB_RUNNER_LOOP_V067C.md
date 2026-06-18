# K-OS Autonomous Job Runner Loop v0.67C

Status: local safe loop.

Comando manual:
powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomous_job_runner_loop.ps1

Comando smoke:
powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomous_job_runner_loop.ps1 -Once

Regras:
- Respeita Autonomy Kill Switch.
- Executa somente jobs seguros do 67B.
- Nao publica Instagram.
- Nao usa IA paga.
- Nao usa navegador logado.
