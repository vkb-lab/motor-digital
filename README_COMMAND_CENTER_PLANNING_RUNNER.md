# Checkpoint 61 - Command Center Planning Runner

Transforma tarefas importadas no Command Center em planos operacionais supervisionados.

## Faz

- le memory/command_center/mission_intake_queue.json
- encontra tarefas queued_for_planning
- gera planos operacionais
- salva planning_queue.json
- marca tarefas como planned_waiting_human_review
- registra eventos
- gera relatorio JSON e Markdown

## Nao faz

- nao executa comandos
- nao chama API externa
- nao publica
- nao envia WhatsApp
- nao faz deploy
- nao usa token
- nao automatiza navegador

## Pagina

pages/42_K_Atlas_Command_Center_Planning_Runner.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_command_center_planning_runner_demo.ps1"
