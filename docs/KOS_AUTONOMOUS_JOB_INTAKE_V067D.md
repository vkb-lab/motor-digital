# K-OS Autonomous Job Intake v0.67D

## Criar job seguro

powershell -ExecutionPolicy Bypass -File scripts\create_kos_autonomous_job.ps1 -Message "teste operacional"

## Regras

- Cria somente jobs write_json_report.
- Respeita Kill Switch.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
