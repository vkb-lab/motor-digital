# KOS GMAIL OPERATOR PREP REPORT

Data: 20260624_201004

## Entrega

Baú preparado para Gmail Operator.

Arquivos:
- memory/kos_governance/KOS_GOOGLE_WORKSPACE_CONNECTION_REGISTRY.json
- memory/kos_governance/KOS_GOOGLE_GMAIL_OPERATOR_CONNECTOR_V1.md
- memory/kos_skills/KOS_SKILL_GMAIL_OPERATOR_V1.md
- scripts/run_gmail_operator.py

## Proximo passo manual

1. Google Cloud Console
2. Projeto: buoyant-song-491421-v6
3. OAuth App: kaizen-home
4. Habilitar Gmail API
5. Baixar OAuth Client JSON
6. Salvar localmente como:
   local_runtime/google_oauth/client_secret.json

Nunca commitar esse arquivo.

## Instalar libs

python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## Autorizar Gmail

python scripts\run_gmail_operator.py --mode connect --profile rogger --scope-preset operator

## Gerar relatorio

python scripts\run_gmail_operator.py --mode report --profile rogger --scope-preset operator --query "newer_than:7d" --max-results 20

## Enviar email

python scripts\run_gmail_operator.py --mode send --profile rogger --scope-preset operator --to "email@exemplo.com" --subject "Assunto" --body "Mensagem" --confirm SEND_GMAIL

## Mover para lixeira

python scripts\run_gmail_operator.py --mode trash --profile rogger --message-id "<MESSAGE_ID>" --confirm TRASH_GMAIL

## Delete permanente

Bloqueado por padrao.
Exige:
--scope-preset full_delete
--allow-permanent-delete
--confirm PERMANENT_DELETE_GMAIL
