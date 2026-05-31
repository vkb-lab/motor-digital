# K-OS Onboarding and Activation Gate

Checkpoint 030.

Objetivo:

- validar tudo antes de ativar cliente
- checar CRM
- checar assinatura
- checar licença
- checar proposta aprovada
- checar deal aprovado
- checar risco
- checar permissões do agente
- bloquear ativação sem gates
- gerar pacote de onboarding

## Regra central

Este checkpoint não ativa cliente de verdade.

Ele apenas:

- valida gates
- cria blockers
- gera onboarding case
- gera pacote de onboarding
- preserva auditoria
- exige aprovação humana

## Antes de ativar cliente

- cliente existe no CRM
- assinatura ativa ou trial aprovado
- License Gate ativo
- deal comercialmente aprovado
- proposta aprovada ou aceita
- matriz de permissão válida
- classificador de risco válido
- Security Firewall disponível
- Schema Guard disponível
- Incident Runbook disponível
- aprovação humana registrada

## Bloqueado por padrão

- ativação automática
- envio externo
- publicação externa
- chamada real de API
- ativação sem licença
- ativação sem assinatura
- ativação sem proposta aprovada
- commit de dados brutos de cliente
- exclusão de logs

## Próximo checkpoint

031 - K-Customer Success and Delivery Tracker