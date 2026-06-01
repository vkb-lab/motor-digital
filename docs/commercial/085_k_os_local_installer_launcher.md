# 085 - K-OS Local Installer / Launcher Core

Gerado em: 2026-06-01T13:23:02Z

## Objetivo

Criar instalador/launcher local seguro do K-OS com manifesto, scripts PowerShell de checagem e inicializacao do cockpit, evidencias sanitizadas e dashboard somente leitura, sem instalar dependencias automaticamente, sem executar installer real, sem deploy, recovery, rollback, drill, reset, force push, limpeza destrutiva ou auto-fix.

## Status

- Checkpoint: 085
- Camada: K-OS Core
- Status do launcher: ready_with_warnings
- Checkpoint anterior: 084 - K-OS Release Candidate Gate Core
- Proximo checkpoint: 086 - K-OS Final Documentation Pack Core

## Scripts criados

| Script | Existe | Politica | SHA256 |
|---|---|---|---|
| scripts/k_os_local_install_check.ps1 | True | ready | 19e0cbaa53675eca67530cca69677e280957dae636e5c21d12f3f107a09b561b |
| scripts/k_os_local_launcher.ps1 | True | ready | 89abcede1e859b667d67772f365f81da7a284ce8c6c300a57e83968e47fc63cc |

## Entrypoint

- Status: ready
- Selecionado: app.py

## Runtime

- Python: 3.13.3
- Streamlit disponivel: False
- requirements.txt possui streamlit: True

## Comandos do operador

Checagem local:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_install_check.ps1
```

Abrir cockpit:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_launcher.ps1
```

## Warnings

- previous_rc_gate_warning

## Garantias de nao execucao

- dependency_install_executed: False
- installer_executed: False
- deploy_executed: False
- release_publish_executed: False
- backup_restore_executed: False
- automatic_remediation_executed: False
- real_drill_executed: False
- real_recovery_executed: False
- real_rollback_executed: False
- git_reset_hard_executed: False
- force_push_executed: False
- destructive_shell_executed: False
- memory_deletion_executed: False
- secret_export_executed: False
- scheduled_task_created: False
- windows_service_created: False
- system_path_modified: False

## Operacoes bloqueadas

- dependency_install_execution
- installer_execution
- deploy_execution
- release_publish_execution
- backup_restore_execution
- real_drill_execution
- real_recovery_execution
- real_rollback_execution
- git_reset_hard
- force_push
- destructive_shell
- memory_deletion
- secret_export
- automatic_remediation

## Decisao operacional

Launcher local criado. O operador pode executar manualmente os scripts quando quiser iniciar o K-OS.
O sistema pode seguir para 086 - K-OS Final Documentation Pack Core.
