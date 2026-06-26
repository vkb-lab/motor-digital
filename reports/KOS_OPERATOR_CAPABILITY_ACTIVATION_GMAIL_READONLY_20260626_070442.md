# K-OS Operator Capability Activation - Gmail Read-Only

Timestamp: 20260626_070442

## Problema Observado

O Operator Chat ja roteava pedidos de Gmail, mas respondia apenas com diagnostico local bloqueado. Isso impedia o uso do `scripts/run_gmail_operator.py` em modo seguro/read-only mesmo quando o Gmail Operator ja existia.

## O Que Foi Ativado

- `gmail_status`: o Operator Chat agora chama localmente:

```powershell
python scripts/run_gmail_operator.py --mode status --profile rogger
```

- `gmail_audit`: o Operator Chat agora chama localmente:

```powershell
python scripts/run_gmail_operator.py --mode report --profile rogger --query "newer_than:7d" --max-results 20
```

- A resposta exibida no chat e limpa:
  - status de conexao;
  - conta mascarada quando houver email;
  - quantidade analisada em relatorio;
  - caminho local do relatorio;
  - sem conteudo bruto de email no corpo do chat.

## O Que Continua Bloqueado

- Enviar email.
- Arquivar email.
- Mover email.
- Marcar email como lido.
- Baixar anexos.
- Deletar email.
- Expor credenciais.
- Colar conteudo bruto de emails no chat.

## O Que Exige Human Gate

- `gmail_archive`
- `gmail_label`
- `gmail_mark_read`
- `gmail_download_attachment`
- `drive_create_folder`
- `drive_move_file`
- `local_file_hash_scan`
- `local_file_rename`

## Policy Criada

Arquivo:

```text
memory/kos_governance/KOS_OPERATOR_CAPABILITY_POLICY.json
```

Categorias:

- `allowed_readonly`
- `requires_human_gate`
- `blocked`

## Comandos Executados

```powershell
python -m py_compile scripts/kos_operator_intent_router.py pages/KOS_Operator_Chat.py
python -m pytest tests/test_kos_operator_intent_router.py tests/test_kos_operator_intent_router_integration.py tests/test_kos_operator_capability_policy.py tests/test_kos_operator_gmail_readonly_execution.py -q
python -m pytest tests/test_kos_local_home_resolver.py tests/test_kos_custom_navigation_applied.py -q
```

## Como Testar no Navegador

1. Abrir o K-OS Local Command Center.
2. Entrar no `KOS Operator Chat`.
3. Enviar: `verifique meu email`.
4. Confirmar resposta de Gmail status sem conteudo de email.
5. Enviar: `audite meus emails recentes`.
6. Confirmar que o chat mostra quantidade/caminho de relatorio, sem colar emails brutos.
7. Enviar: `apague emails antigos`.
8. Confirmar bloqueio por Human Gate.

## Proximos Passos

- Criar renderizacao dedicada para relatorios Gmail com resumo sem snippet.
- Ligar a policy `KOS_OPERATOR_CAPABILITY_POLICY.json` como fonte de verdade do router.
- Criar testes com fixture de stdout do Gmail Operator para validar UI sem acessar Gmail real.

