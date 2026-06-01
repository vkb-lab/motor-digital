# K-OS - Documentacao Final

Gerado em: 2026-06-01T13:26:49Z

Projeto: K-Atlas / K-OS / motor-digital

## Visao geral

O K-OS e a camada operacional do K-Atlas para coordenacao local de agentes, memoria, modulos, comandos, relatorios, governanca e cockpit Streamlit.

## Estado atual

- Checkpoints consolidados: 079, 080, 081, 082, 083, 084, 085
- Evidencias prontas: 0
- Evidencias com warning: 7
- Entrypoint Streamlit selecionado: app.py

## Documentos principais

- docs/k_os/README_K_OS.md
- docs/k_os/OPERATOR_GUIDE.md
- docs/k_os/ARCHITECTURE.md
- docs/k_os/GOVERNANCE.md
- docs/k_os/LAUNCHER_GUIDE.md
- docs/k_os/RELEASE_NOTES.md
- docs/k_os/FINAL_DOCUMENTATION_INDEX.md

## Comandos manuais principais

Checagem local:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_install_check.ps1
```

Abrir cockpit:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\k_os_local_launcher.ps1
```
