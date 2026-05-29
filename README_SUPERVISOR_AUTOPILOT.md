# Checkpoint 34 - Supervisor Autopilot

Aprovação assistida para tarefas de baixo risco.

## O que faz

- Lê Supervisor Queue
- Avalia política de risco
- Aprova somente tarefas seguras
- Bloqueia publicação oficial, automação de navegador, massa e segredo em texto puro
- Registra no Event Bus
- Não executa tarefas

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_supervisor_autopilot.ps1"

## Página

pages/15_K_Atlas_Supervisor_Autopilot.py
