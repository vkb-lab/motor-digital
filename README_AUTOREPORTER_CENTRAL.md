# Checkpoint 37 - AutoReporter Central

Gera relatório central do K-Atlas OS.

## Lê

- módulos principais
- páginas Streamlit
- Git status
- últimos commits
- eventos do Control Plane
- filas locais quando existirem
- status de autonomia

## Saídas

- reports/autoreporter/k_atlas_central_report.json
- reports/autoreporter/k_atlas_central_report.md

## Página

pages/18_K_Atlas_AutoReporter_Central.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_autoreporter_central.ps1"
