# K-OS Support Desk and Ticketing Core

Checkpoint 032.

Objetivo:

- registrar tickets
- classificar prioridade
- acompanhar suporte
- ligar ticket a cliente
- ligar ticket a incidente
- ligar ticket a delivery
- criar base de atendimento recorrente

## Regra central

Support Desk é local.

Ele não:

- envia resposta externa automaticamente
- publica ticket externamente
- substitui SLA contratual
- comita dados brutos de ticket
- apaga logs de auditoria

## Dados reais

O registro bruto fica em:

local_secrets/k_os_support/support_ticket_registry.json

Esse arquivo não vai para o GitHub.

Os relatórios em reports/support são sanitizados.

## Antes de fechar ticket

- ticket existe
- operador revisou
- Customer Success revisou se for delivery
- comercial revisou se for billing/license
- incidente revisado se for segurança/dados
- evento de auditoria registrado

## Próximo checkpoint

033 - K-Knowledge Base and Support Playbooks