# K-OS - Launcher Local

Gerado em: 2026-06-01T13:26:49Z

Projeto: K-Atlas / K-OS / motor-digital

## Objetivo

Fornecer comandos manuais para validar e abrir o cockpit local.

## Checagem

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_install_check.ps1
```

## Abrir cockpit

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_launcher.ps1
```

## Entrypoint detectado

- Selecionado: app.py

## Scripts

- scripts/k_os_local_install_check.ps1: exists=True sha256=19e0cbaa53675eca67530cca69677e280957dae636e5c21d12f3f107a09b561b
- scripts/k_os_local_launcher.ps1: exists=True sha256=89abcede1e859b667d67772f365f81da7a284ce8c6c300a57e83968e47fc63cc

## Observacao

O launcher nao deve instalar dependencias automaticamente. Caso falte dependencia, o operador decide manualmente.
