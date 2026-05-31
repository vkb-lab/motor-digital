# K-OS Product Feedback and Feature Request Core

Checkpoint 034.

Objetivo:

- registrar feedback de clientes
- registrar pedidos de melhoria
- ligar feedback a ticket
- ligar feedback a Customer Success
- priorizar features
- classificar impacto
- estimar esforço
- criar backlog de produto
- preparar evolução SaaS

## Regra central

Product Feedback é local.

Ele não:

- publica roadmap externamente
- promete feature ao cliente
- comita feedback bruto
- envia mensagem automática
- marca feature como entregue sem revisão
- apaga logs de auditoria

## Dados reais

O registro bruto fica em:

local_secrets/k_os_product_feedback/product_feedback_registry.json

Esse arquivo não vai para o GitHub.

Os relatórios em reports/product_feedback são sanitizados.

## Antes de compromisso de roadmap

- feature existe
- feedback vinculado revisado
- product owner revisou
- comercial revisou se impactar receita
- segurança revisou se for segurança
- jurídico revisou se for jurídico
- delivery revisou viabilidade
- operador humano aprovou

## Próximo checkpoint

035 - K-Roadmap Planner and Release Notes Core