# Checkpoint 39 - Deploy Pipeline Assistido

Prepara deploy seguro e reversível.

## Faz

- valida app.py
- valida requirements.txt
- lê git status
- prepara plano de deploy
- prepara plano de rollback
- gera relatório

## Não faz

- não faz deploy automático
- não usa API externa
- não altera produção
- não faz force push
- não publica nada

## Página

pages/20_K_Atlas_Deploy_Pipeline.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_deploy_pipeline_check.ps1"
