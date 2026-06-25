# KOS Local Entrypoint Navigation Audit

Timestamp: 2026-06-25 15:11:57 America/Sao_Paulo
Repo: `C:\Users\oi\Desktop\motor-digital`
Branch esperada: `kos/fase-18-render-public-asset-bridge`
Modo: auditoria read-only, sem patch, sem commit, sem delete, sem acoes externas, sem leitura de secrets.

## 1. Veredito executivo

O `localhost:8501` esta desalinhado. A porta TCP em escuta aponta para um processo `streamlit run app_ksocial_gateway.py`, mas a UI observada no navegador abriu `K-Atlas OS`, conteudo compatível com `app.py`, e sidebar automatica com centenas de paginas de `pages/`.

Isso indica conflito de runtime/porta e nao apenas uma home ruim:

- Ha processos Streamlit simultaneos configurados para a porta 8501.
- O processo que aparece como listener TCP e `app_ksocial_gateway.py`.
- A UI renderizada no navegador interno mostrou titulo `K-Atlas OS`, tabs de `app.py` e sidebar automatica do Streamlit.
- O diretorio `pages/` tem 647 paginas e o Streamlit multipage as expõe automaticamente.
- As pecas novas de Render/Gmail/Google Toolbelt/Brain Provider existem no repo, mas praticamente nao aparecem como paginas visiveis do 8501; a integracao visual principal esta em `app_render.py` ou em scripts/relatorios, nao na home local.

Classificacao:

| Area | Classificacao | Motivo |
|---|---|---|
| Home atual 8501 | desalinhado | Processo listener e UI observada divergem; home visivel e `app.py`, mas PID listener e gateway social. |
| Navegacao | desintegrada | 647 paginas expostas por navegacao automatica, misturando K-Atlas, K-Uni, KOS antigo e KOS novo. |
| Pecas novas | parcialmente integradas | Existem e sao testadas, mas entram em `app_render.py`, scripts ou Operator Chat; nao formam home local consolidada. |
| Risco | alto | Ambiguidade de porta + sidebar com paginas operacionais antigas e gates sensiveis confunde operador e aumenta chance de rota errada. |

## 2. Estado Git

Comando: `git --no-pager status --short`

```text
 M k_atlas/saas_factory/products/k-atlas-local-business-copilot/product.json
```

Observacao: alteracao pre-existente, nao criada por esta auditoria. Diff visivel indica apenas `created_at` atualizado:

```diff
-  "created_at": "2026-05-30T00:18:40.642443+00:00",
+  "created_at": "2026-06-25T16:24:58.340210+00:00",
```

Comando: `git branch --show-current`

```text
kos/fase-18-render-public-asset-bridge
```

Comando: `git --no-pager log --oneline --decorate -n 20`

```text
c83f814 (HEAD -> kos/fase-18-render-public-asset-bridge, tag: kos-safe-render-readonly-mobile-runtime-v1, origin/kos/fase-18-render-public-asset-bridge) add kos render read-only mobile runtime
f2cf645 (tag: kos-safe-browser-render-audits-v1) document browser and render cloud runtime audits
0ab68a5 (tag: kos-safe-browser-audit-v1) document first kos browser audit findings
84a29aa (tag: kos-safe-private-sovereign-operator-v1) register kos private sovereign operator doctrine
99929d7 (tag: kos-safe-brain-provider-priority-v1) add kos brain provider priority policy
61ffdea (tag: kos-safe-brain-ai-current-state-v1) document kos brain ai current state
d0a6afb (tag: kos-safe-google-ai-toolbelt-bridge-v1) add google ai toolbelt bridge and working audit
193a428 (tag: kos-safe-google-ai-toolbelt-v1) register google ai toolbelt for kos orchestrator
b57747d (tag: kos-safe-gmail-real-connected-v1) document gmail real connection status
c25c14e (tag: kos-safe-gmail-next-connection-steps-v1) document next gmail real connection steps
2b7f3e4 (tag: kos-safe-gmail-bau-connector-v1) prepare gmail operator connector and curate chat bau memory
729c07e (tag: kos-safe-real-operator-response-ui-v4) normalize kos operator instagram response ascii
6635f3c (tag: kos-safe-real-operator-response-ui-v3) force clean instagram operator response in ui
bad5afb (tag: kos-safe-real-operator-response-ui-v2) clean kos real operator response formatting
47c51b0 (tag: kos-safe-real-operator-response-ui-v1) render kos operator response as real operational answer
ec201b4 (tag: kos-safe-operator-chat-solidified-v3) stop tracking generated kos brain gateway runtime result
5f44ce5 (tag: kos-safe-operator-chat-solidified-v2) fix kos brain gateway external action risk detection
54304e2 (tag: kos-safe-operator-chat-solidified-v1) document kos dirty tree triage before operator chat consolidation
b515434 solidify kos operator chat brain routing and ux contract
5a16348 consolidate kos runtime routers and operational scripts
```

Tags `kos-safe-*` mais recentes:

```text
kos-safe-render-readonly-mobile-runtime-v1
kos-safe-browser-render-audits-v1
kos-safe-browser-audit-v1
kos-safe-private-sovereign-operator-v1
kos-safe-brain-provider-priority-v1
kos-safe-brain-ai-current-state-v1
kos-safe-google-ai-toolbelt-bridge-v1
kos-safe-google-ai-toolbelt-v1
kos-safe-gmail-real-connected-v1
kos-safe-gmail-next-connection-steps-v1
kos-safe-gmail-bau-connector-v1
kos-safe-real-operator-response-ui-v4
kos-safe-real-operator-response-ui-v3
kos-safe-real-operator-response-ui-v2
kos-safe-real-operator-response-ui-v1
kos-safe-operator-chat-solidified-v3
kos-safe-operator-chat-solidified-v2
kos-safe-operator-chat-solidified-v1
kos-safe-brain-gateway-contract-v1
kos-safe-project-manifesto-v1
```

## 3. Processo e portas Streamlit

Comando de porta:

```powershell
Get-NetTCPConnection -LocalPort 8501,8502,8503,8523 -State Listen -ErrorAction SilentlyContinue
```

Resultado inicial:

```text
LocalAddress LocalPort State  OwningProcess
0.0.0.0      8501      Listen 17024
```

Comando de processo:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId=17024" | Format-List ProcessId,CommandLine,ExecutablePath
```

Resultado:

```text
ProcessId      : 17024
CommandLine    : "C:\Users\oi\Desktop\motor-digital\venv\Scripts\python.exe" -m streamlit run app_ksocial_gateway.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false --server.runOnSave true
ExecutablePath : C:\Python313\python.exe
```

Portas proximas auditadas depois:

```text
LocalAddress LocalPort State  OwningProcess
0.0.0.0      8501      Listen 17024
0.0.0.0      8507      Listen 2976
0.0.0.0      8512      Listen 4400
0.0.0.0      8514      Listen 11960
0.0.0.0      8515      Listen 16508
```

Processos Streamlit relevantes encontrados:

| PID | Porta declarada | Entrypoint | Observacao |
|---:|---:|---|---|
| 840 / 13668 | 8501 | `app.py` | Processo Streamlit adicional configurado para 8501. |
| 16472 / 17024 | 8501 | `app_ksocial_gateway.py` | Listener TCP observado em 8501. |
| 2976 | 8507 | `local_runtime\operator_command_bridge\operator_bridge_app.py` | Existe, mas nao foi inspecionado internamente por regra de nao mexer em `local_runtime`. |
| 4400 | 8512 | `pages\KOS_Local_Review_Inbox.py` | Runtime auxiliar. |
| 11960 | 8514 | `pages\KOS_Engineer_Handoff_Bridge.py` | Runtime auxiliar. |
| 16508 | 8515 | `pages\KOS_Engineer_Handoff_Queue.py` | Runtime auxiliar. |

Conclusao da porta 8501: ha concorrencia/ambiguidade entre `app.py` e `app_ksocial_gateway.py`; o PID listener imediato e `app_ksocial_gateway.py`, mas a UI observada serviu `app.py`.

## 4. Evidencia do navegador

URL aberta: `http://localhost:8501/`

Resultado DOM visivel:

```text
title: K-Atlas OS
sidebar links iniciais:
- app
- K OS BASE Workspace
- KOS Autonomy Dashboard
- K Social Publishing Gateway
- Etapa 7 Independencia
- K Atlas Control Plane
- K Atlas Lousa Operacional
- K Atlas Social Audit Local
- K Atlas Creative Media Gateway
- K Atlas SaaS Builder
- K Atlas Supervisor Autopilot
- K Atlas Credential Vault
- K Atlas Sandbox API Adapter
- K Atlas AutoReporter Central
- K Atlas SaaS Factory Workflow
- K Atlas Deploy Pipeline
- K Atlas Assisted Autonomy
- K Atlas Local Daemon
- K Atlas Command Center
```

Conteudo inicial observado:

```text
K-Atlas OS
Cockpit operacional local do K-OS / Motor Digital
BASE K-OS | Painel Geral | Status do sistema | Memoria operacional | Executor de agentes | Campanhas | Relatorios | Logs recentes
```

Isso corresponde a `app.py`, nao a `app_ksocial_gateway.py`, cujo titulo seria `K-Social Publishing Gateway`.

Links para `KOS_Operator_Chat` e `KOS_Unified_Command_Cockpit`: existem na sidebar automatica, mas ficam soterrados entre centenas de entradas; nao sao destaque de home.

## 5. Entrypoints existentes

| Arquivo | Existe | Finalidade aparente | Chama qual pagina/modulo | Tipo | Cloud seguro | Local seguro | Decisao recomendada |
|---|---:|---|---|---|---|---|---|
| `app.py` | sim | Cockpit local K-Atlas/KOS antigo com tabs gerais | `render_kos_base_workspace_panel`, agentes, memoria, campanhas, relatorios | home local legada | nao ideal | parcialmente | manter temporariamente, mas substituir como home oficial por resolver consolidado. |
| `app_render.py` | sim | Runtime cloud read-only/mobile | Gmail status, Google Toolbelt, Brain Provider, Browser/Render audits | Render/cloud | sim | sim, mas nao como home local | manter como Render-only ou status cloud espelhado. |
| `app_ksocial_gateway.py` | sim | Gateway social sandbox/test page | `render_social_publishing_gateway_panel()` | local social sandbox | nao | sim com ressalva | nao deve ocupar 8501; mover para porta propria ou pagina agrupada. |
| `streamlit_app.py` | nao | fallback Streamlit | n/a | ausente | n/a | n/a | nao criar sem necessidade. |
| `main.py` | nao | fallback generico | n/a | ausente | n/a | n/a | nao usar. |
| `Home.py` | nao | multipage home | n/a | ausente | n/a | n/a | opcional para patch futuro, mas melhor resolver explicito. |
| `.streamlit/config.toml` | nao encontrado | config global | n/a | ausente | n/a | n/a | criar/usar apenas se patch consolidar navegacao. |
| `render.yaml` | sim | Blueprint Render | `streamlit run app_render.py --server.port $PORT` | cloud | sim | nao e launcher local | manter. |
| `scripts/k_os_local_launcher.ps1` | sim | escolhe `app.py`, `streamlit_app.py` ou `Home.py` | primeiro existente, hoje `app.py` | local launcher | n/a | sim com ressalva | atualizar no patch para home oficial unica. |
| `scripts/start_kos_startup_operational_profile.ps1` | sim | perfil de boot | inicia `app.py` em 8501 e auxiliares | startup local | n/a | perigoso por conflito | corrigir no patch; hoje concorre com gateway social. |
| `ops/run_ksocial_gateway_local.ps1` | sim | inicia K-Social Gateway em 8501 | `app_ksocial_gateway.py` | launcher legado/social | nao | conflito | alterar porta ou aposentar do boot. |
| `ops/start_ksocial_gateway_forever.ps1` | sim | loop forever do gateway social | `app_ksocial_gateway.py` em 8501 | watchdog legado/social | nao | conflito | nao deve disputar 8501. |
| `README.md` | sim | doc antiga Motor Digital/Gemini | recomenda `streamlit run app.py` | documentacao | desatualizada | desatualizada | atualizar depois da consolidacao. |
| `CHECKPOINT.md` | sim | checkpoint K-Atlas Local 2026-05-27 | diz localhost 8501 funcional | historico | n/a | desatualizado | manter como historico, nao como fonte de verdade. |

## 6. Inventario Streamlit

Contagem total em `pages/`: 647 arquivos.

Classificacao por prefixo/nome dominante:

| Categoria | Quantidade | Observacao |
|---|---:|---|
| K Atlas | 394 | Grande massa gerada em 2026-05-29/30; muitos stubs de 600-1200 bytes. |
| K Uni | 104 | Serie K-Uni/Marketplace/Master Navigation; em geral legada ou duplicativa. |
| KOS | 142 | Inclui paginas modernas e tambem series antigas 079-088, 915-976. |
| Other | 7 | Entradas de resiliencia, etapa, social ou nomes sem familia clara. |

Paginas relacionadas aos temas pedidos:

| Tema | Arquivos encontrados | Diagnostico |
|---|---|---|
| Operator Chat | `KOS_Operator_Chat.py` | Critica, moderna, grande, com roteamento por linguagem natural; integrada via sidebar automatica e script dedicado 8523, mas nao promovida como home. |
| Unified Command Cockpit | `KOS_Unified_Command_Cockpit.py` | Critica, candidata a centro; script dedicado 8522; nao integrada como home 8501. |
| Command Center | `23_K_Atlas_Command_Center.py`, `41_K_Atlas_Command_Center_Mission_Intake.py`, `42_K_Atlas_Command_Center_Planning_Runner.py`, `938_K_OS_Command_Center_Action_Router.py` | Duplicado entre K-Atlas antigo e KOS core. |
| Render | nenhuma pagina moderna dedicada; mencoes em K-Atlas e Operator Chat | Estado novo vive em `app_render.py` e relatorios, nao em pagina 8501. |
| Gmail | nenhuma pagina dedicada | Scripts/relatorios existem; app_render le status; Operator Chat menciona conexoes. |
| Google Toolbelt | nenhuma pagina dedicada; apenas `32_K_Atlas_Google_Audiovisual_Sandbox.py` antigo | Registry novo nao tem pagina local propria. |
| Brain Provider | `133_K_Atlas_Local_OS_Brain_Governance.py`, `136_K_Atlas_AgentBrainAuthorizationBridge.py`, `455_K_Atlas_KUniBrainDecisionRouter.py` | Antigos; registry novo nao tem pagina local direta. |
| Mission Queue | `40_K_Atlas_Operator_Mission_Queue.py`, `KOS_Mission_Queue.py` | Duplicado; manter KOS moderno. |
| Runtime Health | `KOS_Runtime_Health.py` | Util, read-only; status Git real se snapshot estiver atualizado. |
| Safe Executor | `KOS_Safe_Executor.py` | Util como sandbox local, mas deve ficar atras de grupo/gate. |
| Approval Gate | 7 paginas, incluindo `KOS_Approval_Gate.py` e gates K-Uni/K-Atlas | Duplicado; manter gate KOS moderno e ocultar legados. |

Tabela analitica de paginas criticas:

| Arquivo | Titulo aparente | Categoria | Status | Motivo |
|---|---|---|---|---|
| `KOS_Operator_Chat.py` | K-OS Operator Chat | KOS | central | Principal interface conversacional, roteia status/capacidades e reduz ruido tecnico. |
| `KOS_Unified_Command_Cockpit.py` | K-OS Unified Cockpit | KOS | central | Melhor candidato a painel operacional consolidado. |
| `app_render.py` | K-OS Cloud Status | KOS/Render | central fora de pages | Exposicao read-only de Gmail, Toolbelt, Brain Provider e auditorias cloud. |
| `KOS_Runtime_Health.py` | KOS Runtime Health | KOS | util | Health read-only; expõe Git dirty por snapshot. |
| `KOS_Mission_Queue.py` | KOS Mission Queue | KOS | util | Fila com aprovacao humana. |
| `KOS_Human_Approval.py` | KOS Human Approval Console | KOS | util | Gate humano auditavel. |
| `KOS_Safe_Executor.py` | KOS Safe Executor Sandbox | KOS | util/perigoso se destacado | Executor allowlist local; precisa contexto e bloqueios claros. |
| `KOS_Social_Ops_Control_Center.py` | K-OS Social Ops | KOS | util | Painel social moderno; nao publica automaticamente. |
| `KOS_Weekly_Operator_Workspace.py` | K-OS Weekly Workspace | KOS | util | Workspace operacional recente. |
| `KOS_User_Launcher.py` | K-OS User Launcher | KOS | util | Launcher web recente, mas nao home final. |
| `000_K_OS_BASE_Workspace.py` | K-OS BASE Workspace | KOS | util/legado | Base KOS dentro da home antiga. |
| `000_KOS_Autonomy_Dashboard.py` | KOS Autonomy Dashboard | KOS | util | Dashboard read-only, mas pode duplicar Runtime Health. |
| `23_K_Atlas_Command_Center.py` | K Atlas Command Center | K Atlas | legado | Centro antigo antes do KOS Unified Cockpit. |
| `999_K_Atlas_K_Uni_Master_Dashboard.py` | vazio/nao capturado | K Uni | legado | Master dashboard antigo, parte da massa K-Uni. |
| `515_K_Atlas_KUniMasterStreamlitRouter.py` | K-Atlas KUni Master Streamlit Router | K Uni | legado/orfao | Nome sugere router, mas o menu atual vem do Streamlit automatico. |
| `07_K_Social_Publishing_Gateway.py` | wrapper social | Other | duplicado | Duplica `app_ksocial_gateway.py`/gateway social. |
| `KOS_Approval_Gate.py` | KOS Approval Gate | KOS | util/perigoso | Gate visivel deve existir, mas nao solto em sidebar gigante. |
| `902/905/912_K_Uni_*Approval_Gate.py` | K-Uni approval gates | K Uni | duplicado | Gates comerciais antigos. |
| `947/963_K_OS_Agent_*Approval_Gate_Core.py` | K-OS core gates | KOS antigo | duplicado | Core granular antigo; agrupar/ocultar. |

## 7. Origem do sidebar gigante

A origem principal e a navegacao automatica multipage do Streamlit via pasta `pages/`.

Evidencias:

- Sidebar mostra links gerados a partir dos nomes dos arquivos em `pages/`, por exemplo `K OS BASE Workspace`, `KOS Autonomy Dashboard`, `K Social Publishing Gateway`, `K Atlas Control Plane`.
- `app.py` nao define `st.sidebar`, `st.navigation` ou `st.Page`; define apenas tabs internas.
- `app_ksocial_gateway.py` tambem nao define sidebar customizado; chama apenas `render_social_publishing_gateway_panel()`.
- `KUniMasterStreamlitRouter` existe como pagina (`515_K_Atlas_KUniMasterStreamlitRouter.py`), mas nao e responsavel pela sidebar global observada.
- O rotulo inicial `app` e tipico do script raiz Streamlit; os demais links derivam de `pages/`.

Conclusao: o menu enorme vem do mecanismo automatico de multipage do Streamlit, amplificado por 647 arquivos em `pages/`, e nao de um router central governado.

## 8. Estado antigo vs novo

Itens novos auditados:

| Item | Existe | Lido por app 8501? | Lido por alguma pagina? | Diagnostico |
|---|---:|---:|---:|---|
| `app_render.py` | sim | nao como home local | n/a | Render/cloud status, nao aparece no 8501. |
| `scripts/run_kos_brain_provider_status.py` | sim | nao diretamente | referenciado por testes/relatorios | Script novo isolado do menu. |
| `scripts/run_google_ai_toolbelt_bridge.py` | sim | nao diretamente | referenciado por testes/relatorios | Script novo isolado; relatorio diz proximo passo conectar ao Operator Chat. |
| `scripts/run_gmail_operator.py` | sim | nao diretamente | referenciado por scripts e relatorios | Tem modos com acoes sensiveis; nao deve ser exposto sem wrapper read-only. |
| `memory/kos_governance/KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json` | sim | nao | `app_render.py`, scripts | Estado novo visivel no Render status, nao na home local. |
| `memory/kos_governance/KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json` | sim | nao | `app_render.py`, scripts | Estado novo visivel no Render status, nao na home local. |
| `reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md` | sim | nao | `app_render.py`, scripts | Status novo fora da home local. |
| `reports/KOS_RENDER_READ_ONLY_MOBILE_RUNTIME_20260625_123741.md` | sim | nao | nao encontrado por `rg` nas paginas | Relatorio criado, nao integrado visualmente. |
| `reports/KOS_CODEX_BROWSER_AUDIT_20260625_092134.md` | sim | nao | `app_render.py` | Cloud status mostra sinal, home local nao. |
| `reports/KOS_RENDER_CLOUD_RUNTIME_AUDIT_20260625_095054.md` | sim | nao | `app_render.py` | Cloud status mostra sinal, home local nao. |

Pagina que deveria expor estes estados localmente: `KOS_Unified_Command_Cockpit.py` ou uma nova home oficial `app.py` consolidada que incorpore os cards read-only de `app_render.py`. O `Operator Chat` tambem deve responder a pedidos naturais sobre esses estados, mas nao deve ser o unico local visual.

## 9. Git sujo: real ou stale/cache?

No momento da auditoria, `git status --short` realmente esta sujo:

```text
 M k_atlas/saas_factory/products/k-atlas-local-business-copilot/product.json
```

Portanto, se a UI mostra "Git sujo", ha base real. Porem:

- `KOS_Runtime_Health.py` e `000_KOS_Autonomy_Dashboard.py` leem snapshots JSON, nao necessariamente `git status` ao vivo.
- `scripts/start_kos_startup_operational_profile.ps1` grava `git_status` em `local_runtime\kos_startup_profile\latest_startup_profile_status.json`.
- Como `local_runtime` nao foi inspecionado, nao foi possivel confirmar se algum widget usa snapshot stale.

Resposta: hoje o Git sujo e real; ainda assim, ha risco de stale/cache em paginas que leem snapshots gravados em runtime local.

## 10. Respostas diretas ao CTO

1. Qual arquivo esta rodando em `localhost:8501`?
   - O listener TCP auditado e `app_ksocial_gateway.py` via PID 17024, mas tambem ha processos `app.py` configurados para 8501. A UI observada renderizou `app.py`.

2. Qual app deveria ser a home oficial local?
   - `KOS_Unified_Command_Cockpit.py` deveria virar o nucleo da home local, promovido por um `app.py`/resolver oficial reduzido. `Operator Chat` deve ser acesso primario, nao home unica.

3. `pages/KOS_Operator_Chat.py` esta integrado ou isolado?
   - Parcialmente integrado. Ele aparece pela sidebar automatica e tem script dedicado em 8523, mas nao esta integrado como destaque/rota oficial da home 8501.

4. `app_render.py` deve aparecer no 8501 ou e so Render?
   - Deve permanecer Render/cloud read-only como runtime separado. O 8501 pode reutilizar seus cards/status sanitizados, mas nao deve rodar `app_render.py` como home local principal.

5. O sidebar gigante vem de onde?
   - Da navegacao automatica do Streamlit lendo `pages/`, nao de um router governado.

6. Quantas paginas existem e quantas sao realmente uteis?
   - Existem 647 paginas. Uteis/visiveis para o nucleo: cerca de 10 a 15. O restante deve ficar oculto, arquivado ou acessivel apenas por busca/diagnostico.

7. O status "Git sujo" vem de estado real ou stale/cache?
   - Estado real no momento: sim, ha um arquivo modificado. Pode haver stale/cache em dashboards que leem snapshot de runtime.

8. O que foi criado depois e nao aparece na home?
   - `app_render.py`, Brain Provider registry/status, Google AI Toolbelt bridge/registry, Gmail Operator/status, auditorias Browser/Render e relatorio Render read-only mobile.

9. Quais tres paginas devem virar o nucleo oficial?
   - `KOS_Unified_Command_Cockpit.py`, `KOS_Operator_Chat.py`, `app_render.py` como bloco/status read-only ou pagina local espelhada.

10. O que deve ser ocultado/aposentado do sidebar?
    - Series K-Atlas numeradas 100-543, K-Uni 901-999/455-543, gates duplicados, paginas de checkpoint antigas 079-088/915-976, wrappers sociais duplicados, stubs de batch factory e command centers antigos.

11. Qual patch minimo consolida tudo?
    - `K-OS Local Home Resolver v1`: fixar 8501 em uma home oficial, esconder/ignorar `pages/` legado do menu principal, expor apenas top 10 paginas, integrar status read-only novos e mover gateway social para porta propria.

## 11. Top 10 paginas que devem permanecer visiveis

1. `pages/KOS_Unified_Command_Cockpit.py`
2. `pages/KOS_Operator_Chat.py`
3. `app_render.py` ou pagina local equivalente `KOS_Render_Read_Only_Status.py`
4. `pages/KOS_Runtime_Health.py`
5. `pages/KOS_Mission_Queue.py`
6. `pages/KOS_Human_Approval.py`
7. `pages/KOS_Safe_Executor.py`
8. `pages/KOS_Social_Ops_Control_Center.py`
9. `pages/KOS_Weekly_Operator_Workspace.py`
10. `pages/KOS_User_Launcher.py`

## 12. Top 10 grupos/paginas a ocultar ou aposentar

1. `pages/134_K_Atlas_AgentRuntimeRegistry.py` ate series `543_K_Atlas_*`: massa gerada de stubs.
2. `pages/901_K_Uni_*` a `912_K_Uni_*`: marketplace antigo.
3. `pages/455_K_Atlas_KUni*` a `543_K_Atlas_KUni*`: master/navigation K-Uni duplicativo.
4. `pages/23_K_Atlas_Command_Center.py`: substituido por Unified Cockpit.
5. `pages/41_K_Atlas_Command_Center_Mission_Intake.py`: substituido por KOS Mission Queue/Unified.
6. `pages/42_K_Atlas_Command_Center_Planning_Runner.py`: substituido por KOS safe routing.
7. `pages/07_K_Social_Publishing_Gateway.py`: wrapper duplicado do gateway social.
8. `pages/902/905/912_K_Uni_*Approval_Gate.py`: gates duplicados.
9. `pages/079_K_OS_*` a `088_K_OS_*`: checkpoint v1 antigo.
10. `pages/915_K_OS_*` a `976_K_OS_*`: core granular antigo; manter acessivel apenas por diagnostico.

## 13. Patch recomendado: K-OS Local Home Resolver v1

Nao implementar nesta auditoria.

Escopo minimo:

1. Eleger `app.py` como resolver oficial de home local e remover concorrencia de porta 8501.
2. Alterar `scripts/start_kos_startup_operational_profile.ps1`, `scripts/k_os_local_launcher.ps1`, `ops/run_ksocial_gateway_local.ps1` e `ops/start_ksocial_gateway_forever.ps1` para nao disputar 8501.
3. Mover K-Social Gateway para porta propria, por exemplo 8520, ou expor como item agrupado.
4. Implementar menu reduzido em home oficial com apenas:
   - Unified Command Cockpit
   - Operator Chat
   - Runtime Health
   - Mission Queue
   - Human Approval
   - Safe Executor
   - Render read-only
   - Brain Provider Status
   - Gmail Status
   - Google Toolbelt
5. Reaproveitar as funcoes read-only de `app_render.py` para cards locais sem duplicar logica sensivel.
6. Criar camada de navegacao governada, sem depender da sidebar automatica de `pages/`.
7. Ocultar paginas legadas por uma destas estrategias:
   - mover para `pages_legacy/`;
   - prefixar com underscore se compativel com Streamlit;
   - criar `Home.py`/`st.navigation` explicito, se a versao instalada suportar;
   - manter pagina de busca/diagnostico para legados, sem sidebar gigante.
8. Atualizar README e CHECKPOINT para apontar para a home oficial real.

Nome sugerido: `K-OS Unified Command Center Consolidation v1`.

## 14. Comandos finais

Comando:

```powershell
python -m py_compile app.py app_render.py
```

Resultado: sem erro.

Comando:

```powershell
python -m pytest tests/test_kos_render_read_only_app.py tests/test_kos_brain_provider_priority.py tests/test_kos_google_ai_toolbelt_bridge.py tests/test_kos_gmail_operator_connector.py -q
```

Resultado:

```text
.............                                                            [100%]
13 passed
```

Comando:

```powershell
git --no-pager status --short
```

Resultado antes da criacao deste relatorio:

```text
 M k_atlas/saas_factory/products/k-atlas-local-business-copilot/product.json
```

Resultado esperado apos salvar este relatorio: o arquivo do relatorio aparece como novo, alem da alteracao pre-existente.

