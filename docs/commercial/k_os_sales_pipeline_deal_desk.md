# K-OS Sales Pipeline and Deal Desk

Checkpoint 028.

Objetivo:

- organizar oportunidades comerciais
- criar funil de vendas
- controlar propostas
- priorizar deals
- registrar valor estimado
- registrar probabilidade
- definir próxima ação comercial
- preparar aprovação antes de fechar cliente

## Regra central

O Deal Desk é local.

Ele não:

- fecha cliente automaticamente
- envia proposta externa
- ativa cliente automaticamente
- altera cobrança real
- revoga licença diretamente

## Dados reais

O pipeline bruto fica em:

local_secrets/k_os_sales/sales_pipeline.json

Esse arquivo não vai para o GitHub.

Os relatórios em reports/sales são sanitizados.

## Antes de marcar cliente como ativo

- cliente existe no CRM
- pedido comercial existe
- revisão jurídica se for pago
- aprovação comercial
- assinatura ativa
- License Gate ativo
- AI Risk Classifier validado
- Agent Permission Matrix validada
- approval humano

## Próximo checkpoint

029 - K-Proposal Factory and Quote Builder