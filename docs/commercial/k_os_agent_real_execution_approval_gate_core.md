# K-OS Agent Real Execution Approval Gate Core

Checkpoint 047.

Objetivo:

- aprovar ou bloquear execução real
- validar dry-run anterior
- exigir decisão humana
- registrar decisão auditável
- gerar autorização local
- preparar execução real governada
- impedir ação real sem gate

## Regra central

Este gate não executa ação real.

Ele apenas cria decisão:

- aprovada
- bloqueada
- revogada

A autorização completa fica somente em:

local_secrets/k_os_real_execution_gate/agent_real_execution_approval_gate_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

Os relatórios públicos incluem apenas hash da autorização local.

Não incluem a autorização completa.

## Bloqueios

- executar ação real
- gerar efeito real
- enviar mensagem externa
- publicar conteúdo externo
- chamar provedor externo
- aprovar sem dry-run
- aprovar sem validação
- aprovar sem operador
- commitar estado local bruto

## Próximo checkpoint

048 - K-Agent Safe Execution Router Core