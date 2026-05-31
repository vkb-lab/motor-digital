# K-OS Proposal Factory and Quote Builder

Checkpoint 029.

Objetivo:

- gerar propostas comerciais padronizadas
- gerar orçamentos
- ligar proposta ao deal
- ligar proposta ao CRM
- ligar proposta à assinatura
- ligar proposta à licença
- criar approval gate antes de envio
- manter tudo local até aprovação humana

## Regra central

A Proposal Factory é local.

Ela não:

- envia proposta ao cliente automaticamente
- publica proposta externamente
- ativa cliente
- cria cobrança real
- altera licença diretamente

## Dados reais

O registro bruto de propostas fica em:

local_secrets/k_os_proposals/proposal_registry.json

Esse arquivo não vai para o GitHub.

Os relatórios em reports/proposals são sanitizados.

## Antes de envio manual

- proposta existe
- deal existe
- cliente existe no CRM
- totais validados
- aprovação comercial
- revisão jurídica se pago
- AI Risk Classifier validado
- aprovação humana

## Próximo checkpoint

030 - K-Onboarding and Activation Gate