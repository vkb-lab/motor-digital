# Checkpoint 106 - Download Intake UX Fix

O objetivo deste checkpoint e reduzir atrito operacional no fluxo de instaladores locais.

## Novo fluxo

1. Baixar arquivo K_ATLAS_*.ps1 no chat.
2. Voltar para o PowerShell principal.
3. Executar sempre o mesmo comando:

```powershell
cd "C:\Users\oi\Desktop\motor-digital"; powershell -ExecutionPolicy Bypass -File ".\ops\k_next.ps1"
```

## O que foi criado

- ops/k_next.ps1
- ops/start_k_atlas_download_intake.ps1 atualizado
- pages/106_K_Atlas_Download_Intake_UX.py
- k_atlas/core/download_intake_ux
- relatorios locais em reports/download_intake_ux

## Guardrails

- nao executa automaticamente sem comando humano
- nao abre acesso remoto
- nao chama API externa
- nao publica
- nao envia mensagens
- nao controla mouse
