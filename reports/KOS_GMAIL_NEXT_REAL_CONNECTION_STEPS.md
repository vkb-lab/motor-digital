# KOS Gmail Next Real Connection Steps

Data: 2026-06-24
Status: proxima execucao real pendente de credencial local

## 1. Status atual do conector Gmail

O Gmail Operator esta preparado em modo seguro.
O modo `status` executa sem exigir OAuth e reporta dependencias, presenca de `client_secret.json` e presenca de token local por profile.

Resultado atual para o profile `rogger`:

- `client_secret_present`: false
- `token_present`: false
- `next_step`: connect

## 2. O que ja esta pronto

- Registro Google Workspace salvo em `memory/kos_governance/KOS_GOOGLE_WORKSPACE_CONNECTION_REGISTRY.json`.
- Governanca do Gmail Operator salva em `memory/kos_governance/KOS_GOOGLE_GMAIL_OPERATOR_CONNECTOR_V1.md`.
- Skill operacional salva em `memory/kos_skills/KOS_SKILL_GMAIL_OPERATOR_V1.md`.
- Runner local salvo em `scripts/run_gmail_operator.py`.
- Testes dedicados salvos em `tests/test_kos_gmail_operator_connector.py`.
- `CHAT.txt` bruto e runtime OAuth local protegidos por `.gitignore`.

## 3. O que falta para conexao real

Salvar manualmente o OAuth client secret baixado do Google Cloud no caminho local ignorado pelo Git.

Projeto Google Cloud: `buoyant-song-491421-v6`
OAuth app: `kaizen-home`
API requerida: Gmail API habilitada

Nao criar OAuth fake.
Nao commitar `client_secret.json`.
Nao commitar token local.

## 4. Instalar libs

```powershell
python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 5. Onde colocar o client_secret

```text
local_runtime/google_oauth/client_secret.json
```

## 6. Comando para conectar

```powershell
python scripts\run_gmail_operator.py --mode connect --profile rogger --scope-preset operator
```

## 7. Comando para relatorio

```powershell
python scripts\run_gmail_operator.py --mode report --profile rogger --scope-preset operator --query "newer_than:7d" --max-results 20
```

## 8. Guardrails

- Exigir `SEND_GMAIL` para envio.
- Exigir `TRASH_GMAIL` para mover mensagens para lixeira.
- Exigir `PERMANENT_DELETE_GMAIL` e scope preset `full_delete` para delete permanente.
- Preferir lixeira a delete permanente.
- Nunca commitar token, `client_secret.json`, secrets ou dumps brutos.
- Manter `local_runtime/google_oauth/` local e ignorado pelo Git.
