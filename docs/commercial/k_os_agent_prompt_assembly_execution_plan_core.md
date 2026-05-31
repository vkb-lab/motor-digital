# K-OS Agent Prompt Assembly and Execution Plan Core

Checkpoint 045.

Objetivo:

- montar prompt operacional do agente
- usar pacote de contexto validado
- criar plano de execução
- separar objetivo, contexto, restrições e saída esperada
- bloquear prompt com payload bruto
- gerar execução em dry-run
- preparar agentes para execução real governada

## Regra central

Prompt Assembly não executa ações reais.

Ele prepara:

- identidade do agente
- objetivo da tarefa
- contexto sanitizado
- restrições
- ações permitidas
- plano de execução
- saída esperada
- gates de segurança

## Bloqueios

- payload bruto
- secrets
- token
- api key
- publicação externa
- envio externo
- execução real sem approval

## Estado local

local_secrets/k_os_prompt_assembly/agent_prompt_assembly_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/prompt_assembly/latest_agent_prompt_assembly_report.json
reports/prompt_assembly/latest_agent_prompt_package.json
reports/prompt_assembly/latest_agent_execution_plan.json
reports/prompt_assembly/latest_prompt_assembly_validation_report.json

## Próximo checkpoint

046 - K-Agent Dry Run Executor Core