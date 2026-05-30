# Checkpoint 70 - Manual Apply Rollback Executor

Rollback manual supervisionado para alteracoes aplicadas pelo Manual Apply Executor.

## Faz

- le memory/manual_apply_executor/apply_manifest.json
- roda dry-run de rollback
- restaura backups quando existem
- remove arquivos criados quando nao havia backup
- registra rollback_manifest.json
- gera relatorio JSON e Markdown

## Nao faz

- nao publica
- nao envia mensagem
- nao faz deploy
- nao chama API externa
- nao usa token em texto puro
- nao automatiza navegador
- nao move mouse

## Pagina

pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py

## Demo

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_manual_apply_rollback_executor_demo.ps1"
