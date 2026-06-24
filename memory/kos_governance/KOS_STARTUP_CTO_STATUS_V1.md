# K-OS CTO Audit Fast V1

Gerado em: 2026-06-24 10:43:44

## Estado Git
- Branch: kos/fase-18-render-public-asset-bridge
- Head: 2739ca1 K-OS whitelist local safe creative routes
- Status: sujo

## O que evoluimos
- Operator Chat virou entrada principal.
- Roteador escolhe rotas reais.
- Guardrails bloqueiam publicação e ações externas.
- Hupmix virou caso-escola, não centro do K-OS.
- Pacote Manus foi importado como referência criativa reutilizável.
- GP_VIDEO_02 ganhou score, briefing, prompt pack e preview Manus-compatible.
- Importador Manus foi tornado idempotente para não sujar Git.

## O que já conseguimos fazer
- Ler e auditar Instagram/Hupmix via Meta read-only.
- Baixar asset real do Instagram.
- Criar preview local de vídeo.
- Criar missão de captação.
- Criar memória operacional em JSON/MD.
- Versionar evolução no GitHub.
- Criar skills reutilizáveis.
- Rodar ações locais gateadas pelo Operator Chat.

## O que falta
- Reduzir tela grande e limpar blocos 'Comece por aqui'.
- Centralizar política de rotas seguras.
- Criar banco operacional real.
- Criar painel CTO resumido.
- Ativar Google/Telegram/WhatsApp em modo produção com Human Gate.
- Criar fila de tarefas e logs por agente.
- Criar testes automatizados.
- Preparar deploy reversível.

## Nosso negócio hoje
O K-OS é uma plataforma operacional de IA para pequenos negócios, criadores, agências e times internos que precisam transformar marketing, automação, conteúdo, atendimento e produtos digitais em processos executáveis, auditáveis e reutilizáveis.

## Alvo
Virar uma SaaS/OS de agentes IA capaz de criar campanhas, automações, landing pages, APIs, conteúdo, fluxos comerciais, dashboards e produtos digitais com memória persistente, governança e execução segura.

## Inventário
- Scripts: 241
- Pages Streamlit: 1245
- Memory files: 72
- Reports: 1994
- Campaign files: 16
- Content pack files: 12
- Runtime recent files: 100

## Integrações detectadas
- meta: 9 arquivo(s) com referência
- instagram: 769 arquivo(s) com referência
- google: 16 arquivo(s) com referência
- telegram: 7 arquivo(s) com referência
- manychat: 3 arquivo(s) com referência
- openai: 14 arquivo(s) com referência
- github: 30 arquivo(s) com referência
- streamlit: 710 arquivo(s) com referência
- whatsapp: 46 arquivo(s) com referência

## Segredos detectados sem expor valores
- local_runtime\kos_secrets\meta_access_token.txt: exists=True, tracked_by_git=False
- .env: exists=True, tracked_by_git=False
- .streamlit\secrets.toml: exists=False, tracked_by_git=False
- credentials.json: exists=False, tracked_by_git=False
- token.json: exists=False, tracked_by_git=False
- google_credentials.json: exists=False, tracked_by_git=False
- client_secret.json: exists=False, tracked_by_git=False

## Últimos commits
2739ca1 | 2026-06-24 10:35:41 -0300 | K-OS whitelist local safe creative routes
cfc95e2 | 2026-06-24 10:14:39 -0300 | K-OS make Manus reference import idempotent
59a865e | 2026-06-24 10:07:31 -0300 | K-OS fix Manus import policy and route UI isolation
c8ac04f | 2026-06-24 10:05:11 -0300 | K-OS fix Manus import route priority
8751768 | 2026-06-24 10:01:05 -0300 | K-OS hard gate Manus creative reference import
fc9177a | 2026-06-24 07:00:15 -0300 | K-OS isolate orchestrator route UI
0f73b96 | 2026-06-23 07:38:02 -0300 | K-OS add universal process learning engine
efe198c | 2026-06-23 07:17:51 -0300 | K-OS add Hupmix GP video 02 local video generator
284069e | 2026-06-22 18:51:38 -0300 | K-OS add Hupmix GP video 02 Instagram asset bridge
f3ad0b6 | 2026-06-22 18:41:45 -0300 | K-OS fix runtime boundary for capability executor
360b207 | 2026-06-22 18:33:23 -0300 | K-OS add Hupmix GP video 02 capture mission
d53ef0a | 2026-06-22 18:17:08 -0300 | K-OS add orchestrator mode v1
547589c | 2026-06-22 17:27:22 -0300 | K-OS add capability executor v1
910f604 | 2026-06-22 17:15:12 -0300 | K-OS connect Operator Chat to capability registry
8ffd10d | 2026-06-22 17:12:57 -0300 | K-OS add operational master audit and capability registry
045a1da | 2026-06-22 16:41:37 -0300 | K-OS switch Hupmix GP video 02 to real asset production
6a53c98 | 2026-06-22 16:29:14 -0300 | K-OS fix Hupmix GP video 02 visual panel duplication
5c95a06 | 2026-06-22 16:22:41 -0300 | K-OS prioritize Hupmix GP video 02 production gate
c6471cf | 2026-06-22 16:14:18 -0300 | K-OS add Hupmix GP video 02 continuity production
1781298 | 2026-06-22 16:10:17 -0300 | K-OS persist Hupmix latest publication review report
799e2c6 | 2026-06-22 14:46:20 -0300 | K-OS add Hupmix Garoto Oxy history review panel
eff6c0e | 2026-06-22 14:44:53 -0300 | K-OS add Hupmix Instagram continuity audit
3c5ee7b | 2026-06-22 14:03:55 -0300 | K-OS add Hupmix video publication review gate
ec45381 | 2026-06-22 13:35:06 -0300 | K-OS final operator guard safepoint for video research intake
05c12e6 | 2026-06-22 13:34:22 -0300 | K-OS final operator guard safepoint for video research intake
0eb92e6 | 2026-06-22 13:27:51 -0300 | K-OS compact composer research intake safepoint
d528303 | 2026-06-22 13:15:19 -0300 | K-OS certify research continuity and page lousa
49ee392 | 2026-06-22 13:10:22 -0300 | K-OS add Operator File Intake Center
85cba95 | 2026-06-22 13:05:40 -0300 | K-OS show GP video lousa inline in Operator Chat
e1d1332 | 2026-06-22 12:58:57 -0300 | K-OS make GP video lousa read-only with MP4 preview
931dbbd | 2026-06-22 12:51:29 -0300 | K-OS add Hupmix GP video factory free mode
2b79cde | 2026-06-22 12:49:12 -0300 | K-OS audit Hupmix GP video state
44b7e6f | 2026-06-22 12:43:48 -0300 | K-OS make Operator Chat diagnostic read-only v3
b6962b6 | 2026-06-22 12:25:37 -0300 | K-OS add Operator Chat flow diagnostic panel
66e8efe | 2026-06-22 12:16:14 -0300 | K-OS add resilient operator flow audit
e761336 | 2026-06-22 12:06:11 -0300 | K-OS add codebase static map digest
b68ad0f | 2026-06-22 11:48:17 -0300 | K-OS add internal codebase static map
d1278d4 | 2026-06-22 11:44:56 -0300 | K-OS audit Codebase Memory MCP installer risk
bbb2649 | 2026-06-22 11:42:05 -0300 | K-OS audit Codebase Memory MCP manifests
0a06354 | 2026-06-22 11:28:14 -0300 | K-OS inspect Codebase Memory MCP local readiness
e36c4d0 | 2026-06-22 11:26:07 -0300 | K-OS audit AI tools phase 1 readiness
f1cba93 | 2026-06-22 11:23:29 -0300 | K-OS audit AI tools infrastructure phase 1
86add05 | 2026-06-22 09:23:51 -0300 | K-OS Operator Chat persist GP video lousa render
4c0062b | 2026-06-22 09:17:41 -0300 | K-OS Operator Chat fix GP video MP4 center preview
396422a | 2026-06-22 09:12:31 -0300 | K-OS Operator Chat add Hupmix GP video MP4 preview
95c0771 | 2026-06-22 09:05:25 -0300 | K-OS Operator Chat add Hupmix GP video visual preview
9a94ce4 | 2026-06-22 08:41:34 -0300 | K-OS Operator Chat stabilize GP video kit and render lousa
dec1e0f | 2026-06-22 08:14:45 -0300 | K-OS Operator Chat add Hupmix GP video approval board
af0c348 | 2026-06-22 08:07:32 -0300 | K-OS Operator Mode connect Hupmix GP video 01 production kit
68666e3 | 2026-06-22 08:00:21 -0300 | K-OS Operator Mode connect Hupmix GP continuity package
823f8a0 | 2026-06-22 07:57:27 -0300 | K-OS Hupmix GP campaign continuity package
64e6c22 | 2026-06-22 07:40:16 -0300 | K-OS Operator Mode connect Hupmix social read to Meta Graph
244d778 | 2026-06-22 07:32:25 -0300 | K-OS Operator Mode Hupmix official audit hotfixes
0b258e6 | 2026-06-20 16:39:03 -0300 | K-OS Operator Mode social read intent hotfix
5e252ff | 2026-06-20 16:26:31 -0300 | K-OS Operator Mode missing builders hotfix v2
de5ba0f | 2026-06-20 16:20:39 -0300 | K-OS Operator Mode real agent status hotfix
c119b54 | 2026-06-20 16:11:53 -0300 | K-OS Operator Mode UI state render hotfix
46402d4 | 2026-06-20 16:06:28 -0300 | K-OS Operator Mode gate2 draft state hotfix
c7b3fe5 | 2026-06-20 15:44:24 -0300 | K-OS Operator Mode baseline
b9acdc8 | 2026-06-20 15:32:36 -0300 | K-OS Fase 72J operator home clean state
67a3c24 | 2026-06-20 15:29:35 -0300 | K-OS Fase 72I safe action open button
db3a2c7 | 2026-06-20 15:27:12 -0300 | K-OS Fase 72H safe action history panel
51e1414 | 2026-06-20 15:22:15 -0300 | K-OS Fase 72G safe action buttons
fddcea5 | 2026-06-20 14:37:16 -0300 | K-OS Fase 72F.4 safe details UX
6af55c0 | 2026-06-20 14:32:34 -0300 | K-OS Fase 72F.3 fix UTF-8 action router output
3be9bdf | 2026-06-20 14:30:40 -0300 | K-OS Fase 72F.2 fix action router newline syntax
54a8588 | 2026-06-20 14:28:57 -0300 | K-OS Fase 72F.1 keep action router runtime out of git noise
96b4895 | 2026-06-20 14:26:33 -0300 | K-OS Fase 72F orchestrator action router
15fc9b1 | 2026-06-20 14:12:49 -0300 | K-OS Fase 72E single window operator mode
1ff965c | 2026-06-20 12:17:51 -0300 | K-OS Fase 72D operator chat frontdoor
3767ba8 | 2026-06-20 11:59:21 -0300 | K-OS Fase 72C orchestrator request box
94bdab1 | 2026-06-20 11:50:31 -0300 | K-OS Fase 72B unified command cockpit
aeeacf0 | 2026-06-20 11:34:36 -0300 | K-OS Fase 72A weekly operator workspace
9d6d88a | 2026-06-20 10:57:09 -0300 | K-OS Fase 71C social publish readiness auditor
2df2fad | 2026-06-20 10:36:03 -0300 | K-OS Fase 71B social strategy generator
84e333d | 2026-06-20 10:27:45 -0300 | K-OS Fase 71A social ops control center
b131c61 | 2026-06-20 10:20:55 -0300 | K-OS Fase 70.1 ChatGPT local bridge baseline
fffc826 | 2026-06-20 09:49:04 -0300 | K-OS Fase 70E ChatGPT bridge runtime controller
6d7b3ae | 2026-06-20 08:40:17 -0300 | K-OS Fase 70D ChatGPT bridge drop watcher
beaf0e7 | 2026-06-20 08:35:08 -0300 | K-OS Fase 70C ChatGPT conversation bridge
60db273 | 2026-06-20 08:27:07 -0300 | K-OS Fase 70B safe patch review panel
ad25ce9 | 2026-06-20 08:24:07 -0300 | K-OS Fase 70A safe patch proposer
d15b72b | 2026-06-20 08:11:37 -0300 | K-OS Fase 69.1 engineer packet governance baseline
1747ade | 2026-06-20 08:08:05 -0300 | K-OS Fase 69L engineer packet review console
fd63940 | 2026-06-20 07:57:20 -0300 | K-OS Fase 69K engineer packet one-click runner
a55dfc4 | 2026-06-20 07:52:09 -0300 | K-OS Fase 69J engineer packet promotion bridge
9f9cd7b | 2026-06-20 07:49:39 -0300 | K-OS Fase 69I engineer command intake bridge
3305bd4 | 2026-06-20 07:42:52 -0300 | K-OS Fase 69H Hupmix real publish executor
4615c1d | 2026-06-19 12:20:40 -0300 | K-OS Fase 69E2 publish audit visual panel
e8ce915 | 2026-06-19 12:14:48 -0300 | K-OS Fase 69Z requested external action governance baseline
e99fa13 | 2026-06-19 12:11:48 -0300 | K-OS Fase 69G real publish approval ledger
06e1e20 | 2026-06-19 11:55:09 -0300 | K-OS Fase 69F human confirmed publish dry-run gate
ef5fe24 | 2026-06-19 11:21:20 -0300 | K-OS Fase 69F human confirmed publish dry-run gate
54ee8a2 | 2026-06-19 11:13:26 -0300 | K-OS Fase 69E publish audit gate
2f6edb8 | 2026-06-19 09:54:55 -0300 | K-OS Fase 69D Hupmix Instagram audit connector
d3b9e54 | 2026-06-19 09:35:05 -0300 | K-OS Fase 69C requested autonomy action gate
dd2cac7 | 2026-06-19 09:27:07 -0300 | K-OS Fase 69B user friendly local launcher
f10c866 | 2026-06-19 09:18:26 -0300 | K-OS Fase 69A1 market radar runtime recertification
be35601 | 2026-06-19 09:11:27 -0300 | K-OS Fase 69A agent OS market radar dashboard
bdfa1be | 2026-06-19 08:23:12 -0300 | K-OS Fase 68G safe autonomy mission baseline certification
