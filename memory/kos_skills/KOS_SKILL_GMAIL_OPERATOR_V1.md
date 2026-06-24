# KOS SKILL - GMAIL OPERATOR V1

Status: skill operacional
Funcao: ensinar o K-OS a operar Gmail como ferramenta de trabalho do operador

## Objetivo

Transformar Gmail em uma fonte operacional do K-OS.

O K-OS deve conseguir:
- ler emails;
- resumir caixa de entrada;
- detectar urgencias;
- detectar leads;
- detectar boletos/cobrancas;
- detectar oportunidades;
- preparar respostas;
- criar rascunhos;
- enviar respostas com confirmacao;
- organizar labels;
- arquivar;
- mover para lixeira;
- gerar relatorios;
- registrar evidencia sanitizada.

## Fluxo obrigatorio

1. entender pedido;
2. identificar conta/perfil;
3. verificar conexao OAuth;
4. escolher escopo minimo;
5. executar leitura/relatorio quando seguro;
6. preparar resposta/edicao quando solicitado;
7. pedir confirmacao antes de enviar, lixeira ou exclusao;
8. salvar relatorio sanitizado em reports/gmail_operator;
9. ocultar token, segredo e corpo sensivel da resposta principal.

## Comandos naturais

- audite meus emails
- quais emails importantes chegaram hoje
- responda esse email
- prepare uma resposta
- crie um rascunho
- marque como respondido
- arquive esses emails
- mande para lixeira
- apague permanentemente este email
- gere relatorio do Gmail
- encontre leads no Gmail

## Saida esperada

Resposta principal:
- resumo humano;
- prioridades;
- proximas acoes;
- o que pode ser feito com confirmacao.

Detalhes tecnicos:
- message_ids;
- query;
- labels;
- paths de relatorio;
- escopo usado;
- status do token.

## Politica

Leitura e relatorio podem rodar em modo seguro.
Envio exige confirmacao SEND_GMAIL.
Lixeira exige confirmacao TRASH_GMAIL.
Delete permanente exige PERMANENT_DELETE_GMAIL e escopo full_delete.
