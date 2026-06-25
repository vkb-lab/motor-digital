# KOS GMAIL REAL CONNECTION STATUS

Data: 20260625_072919

## Status

Gmail conectado com sucesso ao K-OS.

## Conta

Email: vkb@kaizen-org.com
Mensagens totais: 275
Threads totais: 208
History ID: 36776

## Relatorio inicial

Status: gerado localmente
Mensagens analisadas no ultimo relatorio: 13
Relatorio local Markdown: C:\Users\oi\Desktop\motor-digital\reports\gmail_operator\20260625_071335_report.md
Relatorio local JSON bruto: C:\Users\oi\Desktop\motor-digital\reports\gmail_operator\20260625_071335_report_raw.json

## Seguranca

Os arquivos abaixo ficam somente locais e ignorados pelo Git:

- local_runtime/google_oauth/
- reports/gmail_operator/

Nao versionar:

- client_secret.json
- token_gmail_rogger.json
- refresh_token
- access_token
- relatorios brutos de emails

## Capacidades disponiveis

- ler Gmail
- gerar relatorios
- listar mensagens por query
- ler mensagem especifica
- modificar labels
- arquivar/remover INBOX
- mover para lixeira com confirmacao
- enviar email com confirmacao SEND_GMAIL

## Guardrails

Envio exige: SEND_GMAIL

Mover para lixeira exige: TRASH_GMAIL

Delete permanente segue bloqueado por padrao e exige escopo full_delete + confirmacao forte: PERMANENT_DELETE_GMAIL

## Proximos comandos uteis

Relatorio dos ultimos 7 dias:

python scripts\run_gmail_operator.py --mode report --profile rogger --scope-preset operator --query "newer_than:7d" --max-results 20

Buscar emails nao lidos:

python scripts\run_gmail_operator.py --mode report --profile rogger --scope-preset operator --query "is:unread newer_than:30d" --max-results 20

Buscar possiveis leads:

python scripts\run_gmail_operator.py --mode report --profile rogger --scope-preset operator --query "(lead OR proposta OR orcamento OR contato) newer_than:90d" --max-results 30
