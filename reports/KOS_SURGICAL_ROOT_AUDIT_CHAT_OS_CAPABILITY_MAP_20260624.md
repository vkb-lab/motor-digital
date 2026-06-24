# K-OS Surgical Root Audit - Chat OS + Capability Map

Data: 2026-06-24  
Repositorio: `C:\Users\oi\Desktop\motor-digital`  
Papel: auditoria CTO cirurgica da raiz, corrigindo a leitura anterior sobre Ki-Publica e reposicionando o K-OS como sistema operacional gerador/administrador de produtos.

---

## 1. Correcao de rota

Minha leitura anterior tratou Ki-Publica como se ja existisse como produto bem definido e quase separado. Isso nao esta correto no estado atual do repositorio.

O que existe de verdade:

- K-OS como base operacional ampla.
- K-Social / social ops / publishing gateway / campanhas / approvals.
- Hupmix como caso-escola mais conectado.
- Casa da Limpeza como cliente/configuracao existente em `clients/casa_da_limpeza/permissions.json`.
- Muitas capacidades para gerar SaaS, produto, campanha, publicacao gateada, auditoria e runtime.
- Nenhum Ki-Publica consolidado como modulo unico, produto final ou configuracao registrada no capability registry.

Decisao corrigida:

Ki-Publica nao deve diminuir o K-OS. Ki-Publica deve ser anexado ao K-OS como uma configuracao/capability de produto social-publicador que usa ferramentas do sistema operacional.

O K-OS continua sendo:

- unicorn builder OS;
- gerador de SaaS/produtos;
- administrador de operacoes;
- cockpit de agentes;
- runtime com autonomia progressiva;
- memoria, governanca, approval gate e logs;
- interface natural por chat.

---

## 2. Estado real da raiz

Inventario observado:

- Arquivos no repo por `rg --files`: 5629.
- Arquivos diretos na raiz: 204.
- READMEs diretos na raiz: 151.
- Diretorios diretos em `k_atlas/core`: 477.
- Testes `tests/test_*.py`: 115.
- Arquivos em `reports`: 2006.
- Arquivos em `config`/`configs`: 149 JSON.
- Arquivos em `memory`: 78.
- Paginas Streamlit em `pages`: 647.
- Scripts em `scripts`: 202.
- Arquivos em `ops`: 326.

Leitura CTO:

O K-OS nao e pequeno. Ele esta mais perto de um sistema operacional experimental do que de um app. O risco nao e falta de ambicao. O risco e a falta de um catalogo operacional unico que diga ao chat: "estas sao minhas ferramentas, estes sao meus parametros, este e o nivel de risco, isto eu posso fazer agora, isto preciso pedir confirmacao".

---

## 3. O que funciona agora

### 3.1 Entrada principal

Existe entrada oficial:

- `KOS_START_HERE.cmd`
- chama `scripts/open_kos_operator_chat.ps1`
- abre `pages/KOS_Operator_Chat.py`
- porta: `8523`
- tenta fechar Streamlits antigos e abrir uma unica tela.

Status: vivo.

Problema: ainda existem muitos `.cmd` paralelos na raiz. Eles funcionam, mas competem mentalmente com a ideia de chat unico.

### 3.2 Chat -> Action Packet

Teste executado:

```powershell
python scripts\run_phase72f_orchestrator_action_router.py --request "crie um saas de agenda para clinicas e mostre o plano"
```

Resultado:

- status: `KOS_ACTION_PACKET_READY`
- rota: `products_saas`
- gerou `packet_path` em `local_runtime/kos_action_router/`

Teste executado:

```powershell
python scripts\run_phase72f_orchestrator_action_router.py --request "quero criar campanha para instagram da casa da limpeza"
```

Resultado:

- status: `KOS_ACTION_PACKET_READY`
- rota: `social_publish`
- gerou `packet_path`

Status: vivo.

Problema: a rota social ainda responde como "Redes sociais / Hupmix / campanhas", mesmo quando o pedido fala Casa da Limpeza. O roteador entende social, mas nao entende tenant/produto Ki-Publica/Casa da Limpeza.

### 3.3 Action Packet -> Safe Action

Teste executado:

```powershell
python scripts\run_phase72g_safe_action_executor.py --packet-path local_runtime\kos_action_router\latest_action_packet.json
```

Resultado:

- status: `KOS_SAFE_ACTION_READY`
- gerou JSON e Markdown em `local_runtime/kos_safe_actions/`
- nao publicou;
- nao fez deploy;
- nao gastou IA paga;
- manteve Human Gate.

Status: vivo.

Problema: o resultado para SaaS ainda e generico demais. Ele cria blueprint seguro, mas ainda nao aciona de verdade o Product Factory/SaaS Factory como ferramentas catalogadas.

### 3.4 Capability Executor

Teste executado:

```powershell
python scripts\run_kos_capability_executor.py --request "auditar tudo autonomia capacidades agentes inteligencia" --no-execute
```

Resultado:

- status: `KOS_CAPABILITY_EXECUTOR_PLAN_READY`
- rota: `operational_capability_audit`
- tarefa: `operational_master_audit`

Status: vivo.

Problema: o `KOS_CAPABILITY_REGISTRY.json` possui so 9 capacidades, enquanto o repositorio tem centenas de ferramentas. O executor conhece um subconjunto Hupmix/Manus/process learning, nao o OS inteiro.

---

## 4. O que esta parcialmente funcionando

### 4.1 Operator Chat

Arquivo: `pages/KOS_Operator_Chat.py`

Funcoes boas:

- recebe pedido em texto;
- chama Action Router;
- exibe resposta;
- gera Safe Action;
- le historico;
- bloqueia comandos locais colados;
- mostra lousa/preview para casos Hupmix;
- tem intake de anexos/pesquisa.

Problema cirurgico:

O arquivo virou mistura de:

- chat;
- painel Hupmix;
- lousa visual;
- intake;
- research center;
- capability executor;
- capability registry;
- diagnostics;
- historico;
- botoes.

Isso contradiz o alvo atual do fundador: "somente um chat onde envio e recebo respostas e na tela me mostra o que fez e ali mesmo confirmo ou peço alteração etc, sem botoes".

Decisao:

Preservar as capacidades, mas tirar a UI de paineis do caminho principal. O chat deve chamar tools internas e renderizar cards/respostas/evidencias no fluxo conversacional.

### 4.2 Social / Ki-Publica base

Existe muita base social:

- `k_atlas/social/` com 120 arquivos Python.
- Publishing Gateway.
- Approval queue.
- Campaign factory.
- Creative engine.
- Instagram readiness.
- WhatsApp readiness.
- Social cockpit.
- Reports e campaign packages.

Status: base real, mas fragmentada.

Problemas:

- Ki-Publica nao aparece como produto/capability oficial.
- Casa da Limpeza nao esta ligada a uma rota social propria.
- Action Router usa Hupmix como default.
- O social tem UI/painel, mas nao esta totalmente conectado ao chat como ferramenta.
- Muitos arquivos em `k_atlas/social` tem BOM no inicio; isso pode nao quebrar execucao normal, mas atrapalha AST/auditoria e alguns testes.

### 4.3 Product Factory / SaaS Factory

Existe base real:

- `k_atlas/product_factory/`: 13 arquivos Python, todos parseaveis na auditoria.
- `k_atlas/saas_factory/`: 27 arquivos Python, 26 parseaveis na auditoria.
- Produtos gerados/exemplos:
  - `brics-paraguay-autos`
  - `closet-pilot`
  - `k-atlas-demo-saas`
  - `k-atlas-local-business-copilot`

Status: vivo como laboratorio gerador de produtos.

Problema:

O Action Router aponta comandos internos que nao existem:

- `scripts/run_product_factory.py`
- `scripts/run_saas_product_mission_pack.py`
- `scripts/run_mission_queue_status.py`
- `scripts/run_runtime_control_status.py`
- `scripts/run_chatgpt_bridge_runtime_status.py`
- `scripts/run_weekly_operator_workspace.py`

Esses alvos precisam virar aliases reais ou ser trocados pelos scripts/modulos atuais.

### 4.4 Governanca

Existe muita governanca:

- 149 JSONs em `config`/`configs`.
- politicas de autonomia;
- kill switch;
- approval;
- runtime boundary;
- external sandbox;
- publish gate;
- CRM;
- billing;
- legal;
- rollback;
- recovery;
- resilience.

Status: forte em intencao e superficie de controle.

Problema:

Governanca esta espalhada. O chat nao consulta um policy service unificado. Varias politicas existem como documentos/configs, mas nao necessariamente como decisao automatica aplicada pelo roteador.

---

## 5. O que esta parado ou desconectado

### 5.1 Catalogo incompleto de ferramentas

O maior problema do K-OS hoje:

As ferramentas existem, mas o chat nao tem um mapa completo, versionado e executavel delas.

O `KOS_CAPABILITY_REGISTRY.json` atual registra:

- Operator Chat;
- Hupmix Instagram read-only;
- Hupmix video review;
- Hupmix GP_VIDEO_02;
- file intake;
- research;
- safe action;
- operator flow audit;
- codebase static map.

Mas o sistema possui muito mais:

- Product Factory;
- SaaS Factory;
- Social Campaign Factory;
- Publishing Gateway;
- Mission Queue;
- Autonomy Jobs;
- Safe Patch;
- Command Registry;
- Agent Runtime Registry;
- Agent Capability Registry;
- Approval Console;
- Recovery/rollback/resilience;
- CRM/customer success/billing/legal configs;
- Ki-Publica desejado;
- Casa da Limpeza tenant/config.

Sem esse catalogo, o chat fica limitado apesar do sistema ser grande.

### 5.2 Testes com drift

Teste executado:

```powershell
python -m pytest tests\test_phase72c_orchestrator_request_box.py tests\test_phase72d_operator_chat_frontdoor.py -q
```

Resultado:

- 7 passaram.
- 1 falhou.

Falha:

- `test_phase72d_page_has_single_request_box`
- esperava texto antigo `Pedir ao Orquestrador`.

Leitura:

O teste esta desatualizado em relacao a UX atual, ou a UX mudou sem atualizar contrato. Isso precisa ser corrigido para travar o novo contrato: chat unico, sem botoes operacionais como principal.

### 5.3 Documentacao operacional antiga

`COMANDOS.md` ainda fala:

- `git pull origin main`
- `streamlit run local_dashboard.py`
- `scripts\atlas.ps1`
- `scripts\aprovar.ps1`

Mas a raiz atual aponta para:

- `KOS_START_HERE.cmd`
- `pages/KOS_Operator_Chat.py`
- `scripts/open_kos_operator_chat.ps1`
- branch `kos/fase-18-render-public-asset-bridge`

Leitura:

Documento antigo pode confundir o proximo executor e reabrir o sistema pelo caminho errado.

---

## 6. Arquitetura correta daqui em diante

### 6.1 Interface

Uma unica interface:

```text
Chat K-OS
Usuario escreve pedido
K-OS responde o que entendeu
K-OS mostra o que fez
K-OS mostra evidencia
Usuario confirma, altera, cancela ou manda continuar por texto
```

Sem depender de botoes como experiencia principal.

Botoes podem existir so como fallback tecnico ou acessibilidade, nao como fluxo operacional.

### 6.2 Motor

Por tras do chat:

```text
Chat
-> Intent Router
-> Tenant/Product Resolver
-> Capability Registry
-> Policy Engine
-> Tool Executor
-> Evidence Ledger
-> Human Gate
-> Memory Update
-> Conversational Response
```

### 6.3 Ki-Publica dentro do K-OS

Ki-Publica deve ser registrado como capability pack:

```json
{
  "id": "ki_publica",
  "type": "product_capability_pack",
  "status": "NEEDS_CONNECTION",
  "uses": [
    "social_campaign_factory",
    "publishing_gateway",
    "approval_queue",
    "brand_profile",
    "content_calendar",
    "instagram_readiness",
    "whatsapp_readiness",
    "reporting"
  ],
  "tenants": [
    "casa_da_limpeza",
    "hupmix",
    "parada_atlantida"
  ],
  "interface": "operator_chat_only",
  "human_gate_required": true
}
```

Casa da Limpeza deve virar tenant/config de Ki-Publica, nao rota generica Hupmix.

---

## 7. Status por area

| Area | Status | Diagnostico | Proxima cirurgia |
|---|---|---|---|
| `KOS_START_HERE.cmd` | Vivo | abre chat unico | manter como entrada oficial |
| `open_kos_operator_chat.ps1` | Vivo | fecha Streamlits antigos e abre porta 8523 | adicionar lock/status mais robusto |
| `pages/KOS_Operator_Chat.py` | Vivo, inchado | chat funciona, mas virou painel multiplo | refatorar para chat-first/tool-renderer |
| `run_phase72f_orchestrator_action_router.py` | Vivo, limitado | gera Action Packet | trocar rotas hardcoded por registry |
| `run_phase72g_safe_action_executor.py` | Vivo | gera rascunho seguro | conectar builders reais por capability |
| `run_kos_capability_executor.py` | Vivo, estreito | executa subset Hupmix/Manus/audit | expandir para catalogo real |
| `KOS_CAPABILITY_REGISTRY.json` | Parcial | 9 capacidades | gerar registry completo de tools |
| `k_atlas/social` | Parcial forte | muitas pecas Ki-Publica-like | empacotar como Ki-Publica capability |
| `k_atlas/product_factory` | Vivo | base geradora de produto | conectar ao chat e SaaS route |
| `k_atlas/saas_factory` | Parcial vivo | exemplos/produtos | conectar via aliases reais |
| `config/` | Forte, espalhado | governanca ampla | policy service unico |
| `COMANDOS.md` | Defasado | aponta fluxo antigo | atualizar ou marcar como legado |
| `tests/phase72d` | Drift | contrato antigo | atualizar para chat-only atual |

---

## 8. Ordem cirurgica de execucao

### Fase A - Catalogar sem criar feature

Criar/atualizar:

- `memory/kos_governance/KOS_TOOL_REGISTRY.json`
- `memory/kos_governance/KOS_PRODUCT_CAPABILITY_PACKS.json`
- `memory/kos_governance/KOS_TENANT_REGISTRY.json`

Cada tool deve ter:

- id;
- nome;
- familia;
- caminho;
- comando real;
- parametros;
- input schema simples;
- output esperado;
- risco;
- autonomia;
- policy requerida;
- evidencia gerada;
- status: `alive`, `needs_alias`, `broken`, `legacy`, `concept`;
- teste/smoke associado.

### Fase B - Resolver Ki-Publica

Criar config:

- `config/products/ki_publica.json`
- `config/tenants/casa_da_limpeza.json`

Conectar:

- brand profile;
- calendario;
- conteudo;
- approval;
- publish gateway;
- report;
- social readiness.

### Fase C - Chat-only contract

Atualizar contrato:

- entrada: texto;
- resposta: entendimento + plano + execucao/evidencia;
- confirmacao: texto do usuario;
- alteracao: texto do usuario;
- botoes: fallback secundario.

Atualizar teste `test_phase72d_operator_chat_frontdoor.py`.

### Fase D - Router por registry

Trocar rotas hardcoded por:

```text
pedido -> intent -> product/tenant -> capability -> policy -> tool -> evidence
```

### Fase E - Aliases reais

Criar aliases para comandos anunciados mas ausentes, ou remover os comandos internos do Action Packet.

Prioridade:

- Product Factory;
- SaaS Product Mission Pack;
- Mission Queue status;
- Runtime Control status;
- ChatGPT Bridge status;
- Weekly Operator Workspace.

---

## 9. Comando para o proximo executor

```text
Voce esta assumindo o K-OS como CTO executor senior. Corrija a rota: nao reduza o sistema a Ki-Publica e nao transforme o K-OS em um SaaS pequeno. O K-OS e um sistema operacional gerador e administrador de produtos, SaaS, agentes e operacoes. Ki-Publica deve ser anexado como capability pack/configuracao dentro do K-OS.

Objetivo imediato:
Transformar o K-OS em uma interface chat-first real: o usuario escreve, o K-OS entende, escolhe ferramentas, executa o que for permitido, mostra evidencia na conversa e pede confirmacao/alteracao por texto. Sem depender de botoes como fluxo principal.

Leia antes de agir:
- reports/KOS_SURGICAL_ROOT_AUDIT_CHAT_OS_CAPABILITY_MAP_20260624.md
- reports/KOS_CTO_REALITY_BALANCE_AND_EXECUTOR_COMMAND_20260624.md
- docs/KOS_OPERATOR_CHAT_FRONTDOOR_V072D.md
- memory/kos_governance/KOS_CAPABILITY_REGISTRY.json
- pages/KOS_Operator_Chat.py
- scripts/run_phase72f_orchestrator_action_router.py
- scripts/run_phase72g_safe_action_executor.py
- scripts/run_kos_capability_executor.py
- k_atlas/social/
- k_atlas/product_factory/
- k_atlas/saas_factory/
- config/
- clients/casa_da_limpeza/permissions.json

Primeira tarefa:
Gerar um Tool Registry real do K-OS sem inventar feature nova.

Entregaveis:
1. memory/kos_governance/KOS_TOOL_REGISTRY.json
2. memory/kos_governance/KOS_PRODUCT_CAPABILITY_PACKS.json
3. memory/kos_governance/KOS_TENANT_REGISTRY.json
4. config/products/ki_publica.json
5. config/tenants/casa_da_limpeza.json
6. Atualizacao do Action Router para consultar registry antes de fallback hardcoded
7. Atualizacao do Operator Chat para operar em modo chat-first: confirmar/alterar/cancelar/continuar por texto
8. Atualizacao dos testes do contrato chat-only

Regras:
- Nao remover capacidades existentes.
- Nao diminuir o K-OS.
- Nao vender Ki-Publica como modulo isolado.
- Nao criar botoes novos como fluxo principal.
- Nao publicar, enviar, deletar, deployar ou gastar IA paga sem Human Gate.
- Nao usar Hupmix como default quando o pedido mencionar Casa da Limpeza.
- Nao deixar comandos internos apontarem para scripts inexistentes.
- Tudo que o chat disser que pode usar precisa existir no registry e ter evidencia.

Testes minimos:
- python -m py_compile pages/KOS_Operator_Chat.py scripts/run_phase72f_orchestrator_action_router.py scripts/run_phase72g_safe_action_executor.py scripts/run_kos_capability_executor.py
- python scripts/run_phase72f_orchestrator_action_router.py --request "criar campanha para Casa da Limpeza no Ki-Publica"
- python scripts/run_phase72f_orchestrator_action_router.py --request "criar um SaaS de agenda para clinicas"
- python scripts/run_phase72g_safe_action_executor.py --packet-path local_runtime/kos_action_router/latest_action_packet.json
- python -m pytest tests/test_phase72c_orchestrator_request_box.py tests/test_phase72d_operator_chat_frontdoor.py -q

Resultado esperado:
O K-OS passa a reconhecer suas ferramentas reais, seus produtos/capability packs e seus tenants. O usuario conversa com o OS, e o OS opera as ferramentas por tras com logs, evidencias e confirmacao textual.
```

---

## 10. Frase CTO final

O problema do K-OS nao e estar grande demais.

O problema e que o tamanho dele ainda nao esta devidamente indexado, roteado e conversavel.

Nao cortar o OS. Organizar o OS para que o chat consiga comandar tudo com seguranca.
