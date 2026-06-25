# KOS Local Home Resolver Patch

Timestamp: 2026-06-25 15:22:32 America/Sao_Paulo
Repo: `C:\Users\oi\Desktop\motor-digital`
Branch: `kos/fase-18-render-public-asset-bridge`
Patch: `K-OS Local Home Resolver v1`

## Problema corrigido

A auditoria `reports/KOS_LOCAL_ENTRYPOINT_NAVIGATION_AUDIT_20260625_151157.md` confirmou que `localhost:8501` estava desalinhado:

- havia concorrencia/ambiguidade entre launchers de `app.py` e `app_ksocial_gateway.py`;
- a UI visivel abria `K-Atlas OS`, uma casca local antiga;
- a sidebar automatica do Streamlit expunha 647 arquivos em `pages/`;
- os modulos novos de Gmail, Google Toolbelt, Brain Provider e Render nao apareciam como nucleo oficial.

Este patch transforma `app.py` na home oficial local enxuta do K-OS, sem deletar paginas e sem tentar esconder fisicamente o legado nesta fase.

## Entrypoint oficial

Entrypoint local oficial:

```text
app.py
```

Titulo da home:

```text
K-OS Local Command Center
```

Porta recomendada:

```text
8501
```

## Paginas e blocos do nucleo

O nucleo visivel recomendado agora esta declarado em `app.py` e validado por teste:

1. `pages/KOS_Operator_Chat.py`
2. `pages/KOS_Unified_Command_Cockpit.py`
3. `pages/KOS_Runtime_Health.py`
4. `pages/KOS_Mission_Queue.py`
5. `pages/KOS_Safe_Execution_Review.py`
6. `pages/KOS_Human_Approval.py`
7. `reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md` como card read-only
8. `memory/kos_governance/KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json` como card read-only
9. `memory/kos_governance/KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json` como card read-only
10. `app_render.py` como referencia ao Render read-only mobile runtime

## Status local read-only

Foi criado:

```text
scripts/run_kos_local_home_status.py
```

O script emite JSON sanitizado com:

- branch atual;
- `git status --short` real;
- porta recomendada;
- existencia das paginas/blocos do nucleo;
- existencia dos scripts novos:
  - `scripts/run_kos_brain_provider_status.py`
  - `scripts/run_google_ai_toolbelt_bridge.py`
  - `scripts/run_gmail_operator.py`
- contagem de paginas Streamlit;
- guardrails declarando que nenhuma API Gmail, segredo ou acao externa foi executada.

O script nao chama Gmail API, nao le runtime sensivel e nao executa publicacao/deploy/email.

## O que fica legado

As 647 paginas em `pages/` continuam no repositório e podem continuar aparecendo no sidebar automatico do Streamlit. Este patch apenas cria uma home oficial que deixa o nucleo claro.

Grupos legados indicados na home:

- series K-Atlas numeradas e stubs de batch factory;
- series K-Uni e Marketplace IA;
- command centers antigos;
- approval gates duplicados;
- paginas K-OS core granulares de checkpoints antigos.

## O que nao foi alterado

- Nenhuma pagina em `pages/` foi removida.
- `app_ksocial_gateway.py` nao foi alterado.
- `app_render.py` nao foi alterado.
- Nenhum arquivo em `local_runtime` foi lido ou alterado.
- Nenhum segredo foi exposto.
- Nenhuma acao externa foi executada.
- Nenhum commit foi criado.

## Como testar

Comandos executados:

```powershell
python -m py_compile app.py scripts/run_kos_local_home_status.py
python -m pytest tests/test_kos_local_home_resolver.py -q
python -m pytest tests/test_kos_render_read_only_app.py tests/test_kos_brain_provider_priority.py tests/test_kos_google_ai_toolbelt_bridge.py tests/test_kos_gmail_operator_connector.py -q
```

Resultados:

```text
tests/test_kos_local_home_resolver.py: 5 passed
regressao Render/Brain/Toolbelt/Gmail: 13 passed
```

## Proxima etapa

Proximo patch recomendado:

```text
K-OS Custom Navigation v1
```

Escopo sugerido:

- parar de depender da navegacao automatica da pasta `pages/`;
- expor apenas o nucleo oficial no menu principal;
- mover paginas antigas para navegacao de diagnostico/busca;
- ajustar launchers para impedir que `app_ksocial_gateway.py` dispute a porta 8501;
- manter compatibilidade com URLs existentes enquanto a migracao acontece.

