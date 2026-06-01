# K-OS - Guia Operacional

Gerado em: 2026-06-01T13:26:49Z

Projeto: K-Atlas / K-OS / motor-digital

## Prioridade operacional

1. Validar ambiente local.
2. Abrir cockpit Streamlit.
3. Consultar registries e relatorios.
4. Operar somente com comandos aprovados.
5. Registrar evidencias antes de qualquer mudanca relevante.

## Checagem local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_install_check.ps1
```

## Abrir cockpit

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_launcher.ps1
```

## Regras de seguranca

- Nao subir segredos para GitHub.
- Nao versionar local_secrets.
- Nao versionar memory/runtime.
- Nao executar git reset hard.
- Nao executar force push.
- Nao executar recovery, rollback ou drill real.
- Nao executar comandos destrutivos.

## Continuidade

Proximo checkpoint: 087 - K-OS Final Audit Pack Core.
