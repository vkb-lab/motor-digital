K-Atlas Engineer, contexto operacional atual:

A etapa 63 criou o Human Decision Center local para pacotes do Planning Approval Packager.

Estado atual:
- Centro de decisao humana criado
- Fila local em live/human_decision_center/decision_queue.json
- Decisoes auditaveis em memory/human_decision_center/
- Relatorios em reports/human_decision_center/
- Sem publicacao automatica
- Sem deploy automatico
- Sem API externa real
- Sem navegador automatico
- Sem mouse automatico
- Governanca humana mantida

Missao:
Gerar a etapa 64 do K-Atlas OS.

Objetivo recomendado:
Conectar o resultado da decisao humana ao fluxo seguinte:
- APPROVE permite continuidade interna supervisionada
- DENY bloqueia execucao
- REQUEST_ADJUSTMENTS devolve ao planejador para revisao

Regras obrigatorias:
- responder em portugues
- entregar um unico bloco PowerShell completo
- compativel com Windows PowerShell
- usar UTF-8
- incluir smoke test
- incluir commit
- incluir push
- nao usar navegador automatico
- nao usar mouse automatico
- nao chamar API externa real
- nao publicar nada
- nao fazer deploy automatico
- cada acao importante deve gerar arquivo, log ou relatorio
