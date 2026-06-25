# KOS Render Cloud Runtime Audit

Data: 2026-06-25 09:50 America/Sao_Paulo
Repo: `C:\Users\oi\Desktop\motor-digital`
Branch: `kos/fase-18-render-public-asset-bridge`
Commit atual: `84a29aa`
Escopo: auditoria somente leitura para preparar K-OS Render Cloud Runtime v1. Nenhum deploy executado.

## Resumo executivo

O repo ja tem um `render.yaml` com dois servicos: um web Python/Streamlit em `app.py` e um static site em `public`. Isso prova uma base inicial para Render, mas o Cloud Runtime v1 ainda nao deve subir o K-OS completo.

Classificacao geral:

- `app.py`: precisa patch pequeno
- `public/` e `public_pages/`: candidato a mobile dashboard
- `pages/KOS_Operator_Chat.py`: manter local
- `k_atlas/core/secure_local_api_runtime/server.py`: manter local, candidato a API cloud-safe apos patch
- `k_atlas/worker.py`: candidato a worker, precisa patch pequeno
- scripts read-only de status/auditoria: candidato a cron
- scripts de publicar, apagar, enviar, browser/GUI, Windows task, ChatGPT bridge e local shell: proibido subir ou manter local

## Respostas objetivas

### 1. Existe app web pronto para Render?

Parcial. Existe `app.py`, um Streamlit pequeno com cockpit operacional, e o `render.yaml` ja aponta para:

`streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false`

Classificacao: precisa patch pequeno.

Motivo: a entrada existe e usa `$PORT`, mas o app le/escreve `reports`, `memory` e eventos locais. Em Render isso vira filesystem efemero. Para demo read-only pode subir; para runtime operacional precisa persistencia externa, auth e separacao de dados sensiveis.

### 2. `pages/KOS_Operator_Chat.py` pode rodar em Render ou deve ficar local?

Deve ficar local nesta fase.

Classificacao: manter local.

Evidencias:

- Arquivo grande: 3711 linhas.
- Imports: `streamlit`, `subprocess`, `os`, `urllib`, `scripts`, `pathlib`.
- Chama scripts locais como action router e safe action executor.
- Usa `local_runtime`, `reports`, midia local, historico local, gates locais e paineis de diagnostico.

Risco cloud: pode expor superficies operacionais demais, depender de filesystem local, confundir Render stateless com runtime local e abrir caminho para chamadas externas caso env vars sejam configuradas sem gate extra.

Recomendacao: extrair uma versao `KOS_Operator_Chat_Cloud_ReadOnly.py` ou uma API sanitizada que apenas leia status publico, filas anonimizadas e relatorios aprovados.

### 3. Existe API FastAPI/Flask/Node?

Nao foi encontrada API FastAPI, Flask ou Node pronta. Tambem nao ha `package.json`.

Existe uma API local usando stdlib HTTP:

- `k_atlas/core/secure_local_api_runtime/server.py`
- Endpoints: `/health`, `/state`, `POST /approval-request`
- Bloqueia host diferente de `127.0.0.1`/`localhost`.

Classificacao: manter local; candidato a API cloud-safe apos patch.

Para Render, seria melhor criar uma API FastAPI pequena com auth, CORS restrito e endpoints read-only:

- `GET /health`
- `GET /runtime/status`
- `GET /reports/index`
- `GET /reports/{id}` somente para relatorios sanitizados

### 4. Existe `requirements.txt`/`package.json` correto?

Existe `requirements.txt`; nao existe `package.json`.

Classificacao: precisa patch pequeno.

Problemas:

- Inclui `pyautogui`, `selenium`, `webdriver-manager`: dependencias de browser/GUI/local automation, ruins para web runtime minimo.
- `k_atlas/services/supabase_service.py` importa `supabase`, mas `supabase` nao esta no `requirements.txt`.
- `scripts/run_gmail_operator.py` precisa `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, mas essas dependencias nao estao no `requirements.txt`.
- `requirements.txt` atual serve mais ao runtime local hibrido do que a um Render cloud runtime enxuto.

Recomendacao: criar `requirements-render.txt` separado para v1:

- `streamlit`
- `python-dotenv`
- `requests`
- `pandas` se o dashboard usar dataframe
- `supabase` somente se worker/API cloud usar Supabase
- Google libs somente em worker/cron isolado, nao no web publico inicial

### 5. Quais scripts podem virar Cron Job?

Classificacao: candidato a cron.

Prioridade alta, seguros/read-only:

- `scripts/run_kos_brain_provider_status.py --mode status`
- `scripts/run_google_ai_toolbelt_bridge.py --mode audit`
- `scripts/run_kos_operational_master_audit.py`
- `scripts/run_kos_operator_flow_audit.py`
- `scripts/run_kos_codebase_static_map.py`
- `scripts/run_phase44_runtime_health_check.py`
- `scripts/run_phase47_briefing_scheduler_tick.py`
- `scripts/run_phase42_scheduler_once.py`
- `scripts/run_mission_queue_status.py`
- `scripts/healthcheck.py`

Prioridade media, com cuidado:

- `scripts/run_gmail_operator.py --mode status --profile rogger`
- `scripts/run_gmail_read_only_audit.py` somente se token cloud-safe for explicitamente provisionado e saida for sanitizada.
- `scripts/run_kos_meta_app_diagnostic.py` apenas em read-only e sem token em arquivo.

Nao colocar em cron cloud agora:

- scripts `*_install_*`, `*_confirmed.ps1`, `start_*.ps1`, Windows task/startup folder.
- scripts de publish real, delete, browser, ChatGPT bridge, local command, shell.

### 6. Quais scripts podem virar Background Worker?

Classificacao: candidato a worker.

Bom candidato:

- `k_atlas/worker.py`: loop em Supabase lendo `k_tasks`, atualizando status e salvando report. Precisa patch pequeno para interval por env, desligamento limpo, logs estruturados e evitar `SUPABASE_SERVICE_ROLE_KEY` quando nao necessario.

Candidatos apos endurecimento:

- `scripts/run_phase67b_autonomous_job_runner.py`
- `scripts/run_phase72g_safe_action_executor.py`
- `scripts/run_phase66b_engineer_handoff_queue.py`
- `scripts/run_phase66c_queue_approval_executor.py`
- `k_atlas/core/local_daemon/run_daemon.py`
- `k_atlas/core/command_center/run_scheduler.py`

Restricao: worker de cloud v1 deve operar apenas em filas cloud-safe, sem acesso a `local_runtime`, navegador, Windows, arquivos pessoais, tokens locais ou acao externa real.

### 7. Quais relatorios podem ser expostos no mobile?

Classificacao: candidato a mobile dashboard.

Publicos/seguros em principio:

- `public/kos/status.json`
- `public/kos/index.html`
- `public/kos/phase10_confirmation.html`
- `public_pages/marketplace_ia/index.html`
- relatorios de status que nao tenham segredo: `reports/KOS_OPERATIONAL_MASTER_AUDIT_V1.md`, `reports/KOS_PHASE18_RENDER_PUBLIC_ASSET_BRIDGE_REPORT.md`, `reports/google_ai_toolbelt/*_working_audit.md`

Dashboards bons para mobile apos indice/sanitizacao:

- `reports/analytics/latest_executive_metrics_report.md`
- `reports/cockpit/latest_executive_cockpit_report.md`
- `reports/mission_control/latest_mission_control_status.md`
- `reports/autonomy/autonomy_ladder_status.md`
- `reports/agent_runtime/latest_agent_runtime_heartbeat_report.md`
- `reports/context_api/latest_context_api_catalog.md`
- `reports/crm/latest_customer_registry_report.md` somente se sem PII ou com redacao.

Nao expor sem redacao:

- `reports/gmail_operator/*`
- `reports/deploy_pipeline/*` em massa
- `reports/codex_runs/*`
- qualquer relatorio com email, token, snippets, ids privados, comandos locais ou caminhos pessoais.

### 8. Quais secrets estao bloqueados?

O `.gitignore` bloqueia:

- `.env`
- `.streamlit/secrets.toml`
- `local_runtime/`
- `local_secrets/`
- `secrets/`
- `credentials/`
- `private/`
- `local_runtime/google_oauth/`
- `reports/gmail_operator/`
- `reports/gmail_operator/*_raw.json`
- `logs/`
- partes sensiveis de `memory/`

Classificacao: proibido subir para arquivos locais; configurar como env var no Render somente quando o servico realmente precisar.

Nomes sensiveis detectados, sem valores:

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `KOS_GMAIL_TOKEN_JSON`
- `GMAIL_TOKEN_JSON`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `META_CLIENT_ID`
- `META_CLIENT_SECRET`
- `META_VERIFY_TOKEN`
- `META_ACCESS_TOKEN`
- `KOS_META_ACCESS_TOKEN`
- `INSTAGRAM_ACCESS_TOKEN`
- `GITHUB_TOKEN`
- `VERCEL_TOKEN`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `RENDER_API_KEY`

Observacao critica: ha `.env` local presente. Como boa pratica, revisar se algum segredo real ja foi exposto fora da maquina e revogar/rotacionar antes de cloud.

### 9. Quais env vars seriam necessarias?

Para web minimo em Render:

- `PYTHON_VERSION=3.11.9`
- `KOS_RUNTIME=render`
- `KOS_EXTERNAL_PUBLISH_ENABLED=false`
- `KOS_REAL_PUBLISH_ENABLED=false`
- `KOS_REAL_ADS_ENABLED=false`
- `KOS_REAL_GOOGLE_EDIT_ENABLED=false`
- `KOS_REAL_PAYMENT_ENABLED=false`
- `KOS_LIVE_CONNECTORS_ENABLED=false`
- `KOS_BROWSER_OPERATOR_ENABLED=false`

Para worker Supabase:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` para leitura/escrita limitada, preferivel
- `SUPABASE_SERVICE_ROLE_KEY` somente em worker privado e com escopo justificado
- `KOS_WORKER_INTERVAL_SECONDS`
- `KOS_WORKER_MAX_TASKS_PER_TICK`

Para AI guarded:

- `GEMINI_API_KEY`
- `KOS_AI_GEMINI_ENABLED=false` por padrao
- `KOS_GEMINI_DAILY_REQUEST_BUDGET`
- `KOS_GEMINI_DAILY_TOKEN_BUDGET`
- `KOS_LOCAL_OPENAI_BASE_URL` nao usar em Render se for local
- `KOS_LMSTUDIO_BASE_URL` nao usar em Render se for local

Para Gmail read-only, apenas em cron/worker privado:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `KOS_GMAIL_TOKEN_JSON`
- `KOS_GMAIL_PROFILE=rogger`
- `KOS_GMAIL_READONLY_ONLY=true`

Para Meta/Instagram read-only, apenas se houver caso aprovado:

- `KOS_META_ACCESS_TOKEN`
- `KOS_META_GRAPH_VERSION`
- `INSTAGRAM_ACCOUNT_ID` ou equivalente
- `KOS_REAL_IG_PUBLISH_ENABLED=false`
- `KOS_HUMAN_OK_FOR_IG_REAL` vazio/false

### 10. `render.yaml` ja existe?

Sim.

Classificacao: precisa patch pequeno.

Conteudo atual:

- web `k-atlas-os`, runtime Python, plan free, startCommand Streamlit `app.py`.
- static `k-atlas-assets`, publica `public`.

Problemas para v1:

- `autoDeploy: true` pode ser agressivo para runtime sensivel.
- Nao separa `requirements-render.txt`.
- Nao define workers/cron.
- Nao marca secrets `sync: false`.
- Start command do Streamlit desabilita XSRF protection; isso pode ser aceitavel para prototipo, mas nao para operador sensivel publico.

### 11. Que servicos minimos criar com US$ 500?

Recomendacao conservadora para v1:

1. Web service privado/publico controlado: `kos-mobile-dashboard`
   - Tipo: web
   - Plano: starter/standard pequeno
   - Funcao: dashboard read-only, status, relatorios sanitizados, links publicos.

2. Static site: `kos-public-assets`
   - Tipo: static
   - Funcao: assets aprovados, paginas publicas, status publico.

3. Worker privado: `kos-cloud-worker`
   - Tipo: worker
   - Funcao: processar fila Supabase cloud-safe, sem browser e sem local shell.

4. Cron: `kos-runtime-status-cron`
   - Frequencia: 15-60 min
   - Funcao: brain/provider status, health, toolbelt audit sanitizado.

5. Cron opcional: `kos-gmail-readonly-cron`
   - Frequencia: manual/diario
   - Funcao: status ou triagem sanitizada; sem envio, sem delete.

6. Banco: usar Supabase existente inicialmente.
   - So criar Render Postgres se houver decisao de migrar ledger/fila para Render.

Uso do budget: nao gastar em GPU/paid AI no v1. Priorizar web+worker+cron pequenos, logs, monitoramento e tempo de hardening.

### 12. O que NAO deve subir para a nuvem?

Classificacao: proibido subir.

- `.env` local e qualquer secret file.
- `local_runtime/`
- `local_secrets/`
- `local_runtime/google_oauth/`
- tokens OAuth e `client_secret.json`
- `logs/` locais
- `memory/security/`, sandbox state e dados pessoais.
- `reports/gmail_operator/` e raw Gmail reports.
- `CHAT.txt`
- `KOS_CODEX_AUTOPILOT_PACKAGE/`
- `_local_quarantine/`
- scripts `.ps1` de Windows task/startup/launcher.
- browser automation: Selenium, webdriver-manager, pyautogui, Chrome user profile.
- `pages/KOS_Operator_Chat.py` completo nesta fase.
- scripts de envio Gmail, trash/delete, Instagram publish real, GitHub publish, Vercel/Render deploy action.
- qualquer relatorio com PII, snippet de email, token, refresh token, client secret, caminhos pessoais ou conteudo bruto de inbox.

## Matriz de classificacao

| Item | Classe | Motivo |
|---|---|---|
| `render.yaml` | precisa patch pequeno | Existe e aponta para Streamlit/static, mas falta separar env/secrets/cron/worker. |
| `app.py` | precisa patch pequeno | Web Streamlit simples, bom para demo read-only; precisa auth/persistencia. |
| `public/` | candidato a mobile dashboard | Conteudo estatico ja publicavel se sanitizado. |
| `public_pages/marketplace_ia/` | candidato a mobile dashboard | Landing estatica pronta. |
| `pages/KOS_Operator_Chat.py` | manter local | Subprocess, runtime local, arquivos locais e alto risco operacional. |
| `k_atlas/core/secure_local_api_runtime/server.py` | manter local | Explicitamente localhost-only; pode virar API cloud-safe apos reescrita. |
| `k_atlas/worker.py` | candidato a worker | Loop Supabase claro; precisa deps/env/limites/observabilidade. |
| `scripts/run_kos_brain_provider_status.py` | candidato a cron | Status read-only, sem segredo bruto. |
| `scripts/run_google_ai_toolbelt_bridge.py` | candidato a cron | Gera auditoria/briefing local; expor so output sanitizado. |
| `scripts/run_phase44_runtime_health_check.py` | candidato a cron | Health/status sem acao externa. |
| `scripts/run_phase47_briefing_scheduler_tick.py` | candidato a cron | Tick seguro, desde que output nao dependa de local private data. |
| `scripts/run_gmail_operator.py` | manter local | Modos send/trash/delete existem; em cloud so wrapper read-only isolado. |
| `scripts/run_phase69h_hupmix_real_publish_executor.py` | proibido subir | Executor de publicacao real. |
| `scripts/start_*.ps1` e `scripts/*windows_task*` | proibido subir | Windows/local daemon/startup. |
| `.env`, `local_runtime/`, `local_secrets/` | proibido subir | Segredos e estado local. |
| `requirements.txt` | precisa patch pequeno | Incompleto para Supabase/Gmail e pesado para cloud web. |
| API FastAPI/Flask/Node | nao comprovado | Nao encontrada. |

## Blueprint minimo recomendado para proximo patch

Nao aplicar ainda sem autorizacao.

1. Criar `requirements-render.txt` enxuto.
2. Criar `app_render.py` ou `pages/KOS_Mobile_Status_Dashboard.py` read-only.
3. Criar `scripts/render_cron_status_snapshot.py` que gera somente JSON/MD sanitizado.
4. Criar `worker_render.py` com loop Supabase limitado.
5. Atualizar `render.yaml` com:
   - `kos-mobile-dashboard` web
   - `kos-public-assets` static
   - `kos-cloud-worker` worker
   - `kos-runtime-status-cron` cron
   - secrets com `sync: false`
6. Desativar `autoDeploy` ate v1 estar revisado.

## Veredito

K-OS Render Cloud Runtime v1 esta parcialmente preparado.

Pronto agora:

- Static public assets.
- Streamlit `app.py` para demo read-only simples, com ressalvas.
- Cron read-only de status/auditoria, apos garantir output sanitizado.

Nao pronto:

- Operator Chat completo em Render.
- Gmail/Meta live operators em cloud.
- Worker autonomo com execucao real.
- API publica de operador.

Proximo patch recomendado: separar uma superficie cloud-safe minima (`app_render.py` + `requirements-render.txt` + `render.yaml` revisado) e deixar o Operator Chat local como cockpit privilegiado.
