# Checkpoint 29 - K-Atlas Lousa Operacional

A Lousa Operacional conecta operador, agentes, fila de comandos e PowerShell Runner local.

## Fluxo

mensagem na lousa
-> plano seguro
-> comandos em fila
-> aprovacao humana
-> runner local executa
-> resultado volta para memoria
-> cockpit mostra

## Arquivos

- k_atlas/core/blackboard/blackboard_store.py
- k_atlas/core/blackboard/blackboard_agent.py
- k_atlas/core/blackboard/command_policy.py
- k_atlas/core/blackboard/powershell_runner.py
- pages/11_K_Atlas_Lousa_Operacional.py
- ops/start_blackboard_runner.ps1

## Regra

O Render nao executa PowerShell local.
Para comandos locais, rode o runner no Windows.

## Rodar runner

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\start_blackboard_runner.ps1"