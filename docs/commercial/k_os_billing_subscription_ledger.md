# K-OS Billing and Subscription Ledger

Checkpoint 026.

Objetivo:

- registrar clientes
- registrar planos
- registrar assinaturas
- registrar status de pagamento
- registrar vencimentos
- ligar assinatura ao License Gate
- bloquear ativacao se assinatura nao estiver ativa
- gerar trilha financeira operacional sanitizada

## Regra central

Este checkpoint nao cobra dinheiro de verdade.

Ele nao:

- chama Stripe
- chama PIX
- chama banco
- gera nota fiscal
- gera documento tributario
- executa cobrança externa

Ele apenas cria um ledger operacional local.

## Dados sensiveis

O ledger real fica em:

local_secrets/k_os_billing/billing_ledger.json

Esse arquivo nao vai para o GitHub.

Os relatórios em reports/billing sao sanitizados.

## Ativacao de cliente

Para ativar um agente pago:

- pedido comercial aprovado
- assinatura ativa
- License Gate ativo
- AI Risk Classifier validado
- Agent Permission Matrix validada
- approval humano
- revisao juridica quando exigida

## Suspensao segura

Se assinatura vencer, ficar inadimplente ou nao houver acordo:

- bloquear nova ativacao
- suspender assinatura
- revisar License Gate
- desativar agente se aprovado
- preservar logs
- nao apagar dados de cliente silenciosamente

## Proximo checkpoint

027 - K-Customer Registry and CRM Core