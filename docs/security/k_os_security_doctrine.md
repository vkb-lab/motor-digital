# K-OS Security Doctrine

## Lei operacional

K-OS só evolui com:

- segurança
- validação
- approval gate
- auditoria
- rollback
- evidência documental

## Regras de ouro

1. Nenhum agente decide sozinho.
2. Nenhum dado sensível sobe sem inspeção.
3. Nenhuma API externa roda sem sandbox.
4. Nenhuma publicação sai sem approval gate.
5. Nenhum deploy fica sem rollback.
6. Nenhuma missão fecha sem relatório.
7. Nenhuma credencial deve ser commitada.
8. Nenhum lead bruto deve sair de live/.
9. Nenhum pacote manual real deve ir para GitHub.
10. Toda exceção deve ser registrada.

## Evidências mínimas por missão

- relatório JSON
- relatório Markdown
- evento de auditoria
- status do gate humano
- status de envio externo
- status de publicação externa
- caminho dos artefatos
- responsável humano
- próximo passo recomendado