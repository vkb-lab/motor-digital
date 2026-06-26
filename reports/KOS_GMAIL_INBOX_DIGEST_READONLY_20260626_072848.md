# K-OS Gmail Read-Only Inbox Digest v1

Timestamp: 20260626_072848

## Problema Observado no Print

O Operator Chat respondia a `verifique meu email` apenas com status de conexão, como `Gmail conectado: sim`. Isso confirmava a ponte, mas não entregava valor operacional para Rogger.

## Comportamento Anterior

- `verifique meu email` caía em `gmail_status`.
- O chat mostrava apenas conexão/perfil.
- Nenhum digest da caixa recente era montado.

## Comportamento Novo

- `verifique meu email`, `cheque meu email`, `tem email novo?`, `veja meus emails`, `resuma minha caixa` e `o que chegou no gmail?` agora roteiam para `gmail_digest`.
- O Operator Chat executa localmente, em modo read-only:

```powershell
python scripts/run_gmail_operator.py --mode report --profile rogger --query "newer_than:7d" --max-results 30
```

- A resposta operacional mostra:
  - status do digest;
  - janela dos últimos 7 dias;
  - limite de 30 mensagens;
  - quantidade analisada;
  - mensagens não lidas, se detectadas por labels;
  - anexos detectáveis;
  - destaques por categoria;
  - exemplos seguros com remetente mascarado, assunto e data;
  - caminho local do relatório.

## Categorias do Digest

- oportunidades/startup/crédito
- serviços/infra/dev
- documentos/anexos
- financeiro/cobrança
- promoções/ofertas
- pessoal/família
- outros

## Limites de Segurança

- Não envia email.
- Não deleta email.
- Não arquiva email.
- Não move email.
- Não marca email como lido.
- Não baixa anexos.
- Não expõe credenciais.
- Não cola corpo completo de email no chat.
- Detalhes técnicos permanecem em expansor fechado.

## Como Testar no Navegador

1. Abrir `app.py` no Streamlit local.
2. Entrar no `KOS Operator Chat`.
3. Digitar: `verifique meu email`.
4. Confirmar que aparece `Digest Gmail read-only gerado`.
5. Confirmar que há categorias e exemplos seguros.
6. Digitar: `Gmail está conectado?`.
7. Confirmar que a rota continua sendo apenas status.
8. Digitar: `apague emails antigos`.
9. Confirmar bloqueio por Human Gate.

## Próximos Passos

- Criar fixture local para simular Gmail stdout em testes de renderização.
- Criar tela dedicada para navegar relatórios em `reports/gmail_operator/`.
- Mover categorias e palavras-chave para registry versionado.

