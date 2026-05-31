# K-OS Customer Registry and CRM Core

Checkpoint 027.

Objetivo:

- registrar clientes
- registrar leads
- registrar contatos
- registrar status comercial
- ligar cliente a assinatura
- ligar cliente a licença
- ligar cliente a proposta
- registrar histórico comercial
- preparar CRM interno do K-OS

## Regra central

O CRM real fica local:

local_secrets/k_os_crm/customer_registry.json

Esse arquivo nao vai para o GitHub.

Os relatorios em reports/crm sao sanitizados.

## Bloqueado por padrao

- envio externo sem aprovação
- WhatsApp automatico sem gate
- email automatico sem gate
- publicação externa sem gate
- commit de contatos brutos
- exclusão de dados de cliente sem política
- exclusão de logs de auditoria

## Antes de ativar cliente

- cliente existe no CRM
- assinatura ativa
- License Gate ativo
- pedido comercial aprovado
- AI Risk Classifier validado
- Agent Permission Matrix validada
- approval humano

## Próximo checkpoint

028 - K-Sales Pipeline and Deal Desk