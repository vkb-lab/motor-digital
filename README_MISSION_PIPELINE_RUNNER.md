# Checkpoint 76 - Mission Pipeline Runner

Pipeline local para conectar:

mission pack generator -> mission pack bridge -> local mission installer

## Faz

- descobre componentes dos checkpoints 73, 74 e 75
- cria plano operacional
- roda dry-run sem instalar nada
- oferece script supervisionado para gerar, converter e instalar missao local
- gera relatorio JSON e Markdown
- registra eventos
- exibe painel Streamlit

## Nao faz

- nao chama API externa
- nao publica
- nao envia mensagem
- nao faz deploy
- nao automatiza navegador
- nao move mouse
- nao instala sem aprovacao humana

## Script operacional

Dry-run:

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_mission_pipeline.ps1"

Instalacao supervisionada:

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_mission_pipeline.ps1" -Approve -Install

## Pagina

pages/76_K_Atlas_Mission_Pipeline_Runner.py
