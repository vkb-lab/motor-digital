# K-OS AI Risk Classifier

Checkpoint 021.

Objetivo:

- classificar risco de cada ação de IA
- bloquear ações perigosas por padrão
- exigir approval gate por nível de risco
- preparar AI governance
- preparar venda e assinatura de agentes com permissão K-OS
- preparar Emergency Kill Switch seguro

## Regra comercial

As IAs/agentes podem ser vendidos ou assinados, mas somente com:

- licença ativa
- permissão K-OS
- escopo definido
- plano definido
- approval gate
- auditoria
- possibilidade de revogação

## Autodestrutivo seguro

No K-OS, autodestrutivo não significa destruir dados de cliente.

Significa:

- revogar licença
- desativar agente
- bloquear conectores
- congelar execução
- bloquear novos outputs
- preservar logs
- gerar relatório de incidente

## Proibido por padrão

- apagar dados de cliente silenciosamente
- apagar logs de auditoria
- publicar externamente sem gate
- enviar mensagens sem gate
- acessar chave bruta
- acionar API externa sem sandbox

## Próximo checkpoint

022 - K-External API Sandbox