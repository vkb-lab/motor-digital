# K-OS Agent Safe Execution Router Core

Checkpoint 048.

Objetivo:

- rotear execução aprovada com segurança
- validar aprovação local
- validar hash de autorização
- validar dry-run
- validar permissões
- validar allowlist
- preparar executor allowlisted

## Regra central

O router não executa ação real.

Ele apenas cria rota segura para o próximo executor.

## Permitido

- criar rota sanitizada
- validar aprovação
- validar allowlist
- validar permissão
- registrar evidência
- preparar executor allowlisted

## Bloqueado

- executar efeito real
- enviar mensagem externa
- publicar conteúdo externo
- chamar provedor externo
- exportar segredo
- exportar memória bruta
- executar fora da allowlist

## Estado local

local_secrets/k_os_safe_execution_router/agent_safe_execution_router_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/safe_execution_router/latest_agent_safe_execution_router_report.json
reports/safe_execution_router/latest_safe_execution_route.json
reports/safe_execution_router/latest_safe_execution_route_validation_report.json

## Próximo checkpoint

049 - K-Agent Allowlisted Action Executor Core