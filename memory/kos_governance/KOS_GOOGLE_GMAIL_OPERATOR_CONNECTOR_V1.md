# KOS GOOGLE/GMAIL OPERATOR CONNECTOR V1

Status: preparado para conexao real
Funcao: permitir que o K-OS leia, relate, organize, responda e opere Gmail com autorizacao do operador

## Fontes oficiais

Google Cloud Project: buoyant-song-491421-v6
OAuth App: kaizen-home
API alvo: Gmail API
Token local: local_runtime/google_oauth/token_gmail_<profile>.json
Client secret local esperado: local_runtime/google_oauth/client_secret.json

## O que o K-OS deve conseguir fazer

1. Status da conexao Gmail
2. OAuth local com consentimento do operador
3. Relatorio de caixa de entrada
4. Leitura de emails
5. Classificacao de emails
6. Edicao de labels
7. Arquivar
8. Mover para lixeira
9. Criar rascunho de resposta
10. Enviar email somente com confirmacao textual
11. Excluir permanentemente somente com escopo restrito e confirmacao textual forte

## Niveis de permissao

### Nivel 0 - Status
Verifica se dependencias, client_secret e token existem.

### Nivel 1 - Leitura e relatorio
Lista mensagens, remetentes, assuntos, datas, labels, snippets e gera relatorio sanitizado.

### Nivel 2 - Organizacao
Marca como lido, adiciona/remove labels, arquiva e move para lixeira.

### Nivel 3 - Envio supervisionado
Cria resposta ou envia email apenas com confirmacao:
SEND_GMAIL

### Nivel 4 - Exclusao permanente
Bloqueado por padrao.
Exige:
- escopo https://mail.google.com/
- flag allow-permanent-delete
- confirmacao PERMANENT_DELETE_GMAIL

## Regra de seguranca

O K-OS deve preferir lixeira ao delete permanente.
O K-OS nao deve enviar, apagar ou alterar email sem registro e confirmacao quando a acao for externa ou destrutiva.
Secrets e refresh tokens nunca entram no Git.
