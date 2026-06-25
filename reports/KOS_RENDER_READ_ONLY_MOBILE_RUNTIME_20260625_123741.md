# KOS Render Read-Only Mobile Runtime v1

Data: 2026-06-25 12:37 America/Sao_Paulo
Repo: `C:\Users\oi\Desktop\motor-digital`
Branch: `kos/fase-18-render-public-asset-bridge`
Deploy executado: nao

## O que foi criado

- `app_render.py`: app Streamlit mobile-first e somente leitura para acompanhamento 24/7.
- `requirements-render.txt`: dependencias cloud enxutas, contendo apenas `streamlit`.
- `tests/test_kos_render_read_only_app.py`: testes de contrato para impedir `subprocess`, runtime local, token Gmail, client secret e dependencias extras.

## O que foi alterado

- `render.yaml`: o web service agora usa:
  - `buildCommand: pip install -r requirements-render.txt`
  - `startCommand: streamlit run app_render.py --server.port $PORT --server.address 0.0.0.0`
  - `autoDeploy: false`

## O que fica local

- Operator Chat completo em `pages/KOS_Operator_Chat.py`.
- Baú sensivel, memorias privadas e runtime operacional.
- Gmail API real, envio, delete, modify e raw reports.
- Browser automation, perfis Chrome, Selenium e automacao GUI.
- Scripts PowerShell de Windows task, startup, launchers e loops locais.
- Qualquer execucao real de publish, deploy, email ou patch.

## O que pode ir para Render

- `app_render.py` como web service read-only.
- `public/` como static site.
- Relatorios sanitizados ja versionados e aprovados.
- Registries read-only de governanca que nao contenham segredo.
- Futuramente: cron/worker read-only com saida sanitizada, apos patch separado.

## Env vars necessarias

Minimo para web read-only:

- `PYTHON_VERSION=3.11.9`
- `KOS_RUNTIME=render`
- `KOS_EXTERNAL_PUBLISH_ENABLED=false`
- `KOS_LIVE_CONNECTORS_ENABLED=false`
- `KOS_BROWSER_OPERATOR_ENABLED=false`

Nao ha necessidade de `GEMINI_API_KEY`, Gmail OAuth, Meta token, Supabase ou Render API key para o web read-only v1.

## Secrets proibidos

Nao configurar no web read-only v1:

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `GOOGLE_CLIENT_SECRET`
- `GMAIL_CLIENT_SECRET`
- `KOS_GMAIL_TOKEN_JSON`
- `GMAIL_TOKEN_JSON`
- `SUPABASE_SERVICE_ROLE_KEY`
- `META_CLIENT_SECRET`
- `META_ACCESS_TOKEN`
- `KOS_META_ACCESS_TOKEN`
- `INSTAGRAM_ACCESS_TOKEN`
- `GITHUB_TOKEN`
- `VERCEL_TOKEN`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `RENDER_API_KEY`
- qualquer arquivo de OAuth, token, refresh token, client secret ou `.env`

## Guardrails do app

- Sem envio de email.
- Sem delete.
- Sem publish.
- Sem secrets.
- Sem Baú sensivel.
- Sem runtime local.
- Sem subprocess.
- Sem Gmail API.
- Sem leitura de `.env`.
- Sem execucao externa.

## Como testar local

```powershell
cd "C:\Users\oi\Desktop\motor-digital"
python -m pip install -r requirements-render.txt
python -m py_compile app_render.py
python -m pytest tests\test_kos_render_read_only_app.py -q
python -m streamlit run app_render.py
```

Abrir o URL local exibido pelo Streamlit e validar no mobile/responsivo:

- titulo `K-OS Cloud Status`
- aviso de nucleo soberano local
- cards Gmail, Google AI Toolbelt, Brain Provider Priority, Browser Audit e Render Audit
- proximos passos
- guardrails

## Como fazer deploy manual na Render

Nao feito nesta execucao.

Fluxo recomendado:

1. Revisar `git diff`.
2. Commitar os arquivos do runtime read-only.
3. Push para `origin kos/fase-18-render-public-asset-bridge`.
4. Abrir o Blueprint no Dashboard da Render.
5. Confirmar que o web service usa `app_render.py` e `requirements-render.txt`.
6. Nao inserir secrets no web read-only v1.
7. Aplicar manualmente o Blueprint.
8. Validar `/` no browser mobile.
9. Conferir logs procurando qualquer tentativa de API, segredo ou runtime local.

## Verificacao executada

```txt
python -m py_compile app_render.py
OK

python -m pytest tests/test_kos_render_read_only_app.py -q
... [100%]
```

## Proximo commit sugerido

```txt
add kos render read-only mobile runtime
```
