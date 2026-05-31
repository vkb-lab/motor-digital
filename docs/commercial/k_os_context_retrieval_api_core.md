# K-OS Context Retrieval API Core

Checkpoint 043.

Objetivo:

- criar API local de recuperação de contexto
- consultar memória indexada
- servir contexto para agentes
- filtrar por domínio
- filtrar por módulo
- buscar eventos relevantes
- preparar RAG operacional local
- conectar memória ao cockpit e ao Command Center

## Regra central

A Context Retrieval API é local.

Ela não:

- abre interface pública
- retorna payload bruto
- envia dados externos
- publica contexto
- apaga logs de recuperação
- ignora sanitização

## Endpoints locais

- GET /health
- GET /catalog
- GET /retrieve
- GET /domains
- GET /events
- GET /context

## Abrir API local

powershell -ExecutionPolicy Bypass -File ops\open_k_os_context_retrieval_api.ps1

URL:

http://127.0.0.1:8583

## Exemplo

http://127.0.0.1:8583/retrieve?query=agent&limit=10

## Estado local

local_secrets/k_os_context_api/context_retrieval_api_state.json

Esse arquivo não vai para o GitHub.

## Relatórios sanitizados

reports/context_api/latest_context_retrieval_api_report.json
reports/context_api/latest_context_api_catalog.json
reports/context_api/latest_context_retrieval_report.json

## Próximo checkpoint

044 - K-Agent Context Injection Layer