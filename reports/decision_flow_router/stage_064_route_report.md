# K-Atlas Stage 64 - Decision Flow Router Report

Status: `PASS`
Gerado em: 2026-05-30T05:13:53+00:00

## Objetivo

Conectar decisoes humanas ao fluxo seguinte com governanca local e auditavel.

## Resumo

- Decisoes humanas lidas: 6
- Rotas geradas: 6
- Aprovadas para continuidade supervisionada: 2
- Bloqueadas por negacao humana: 2
- Devolvidas ao planejador para ajustes: 2

## Rotas

### stage_063_demo_adjustments

- Route ID: `route_31c983bd5afc2a95`
- Decisao humana: `REQUEST_ADJUSTMENTS`
- Status humano: `ADJUSTMENTS_REQUESTED`
- Tipo de rota: `PLANNER_REVISION_REQUEST`
- Proxima acao: `REQUEST_PLANNER_ADJUSTMENTS`
- Artefato: `reports/planning_adjustment_requests/stage_064_stage_063_demo_adjustments_adjustment_request.json`

A decisao humana pediu ajustes. O pacote deve voltar ao planejador antes de qualquer continuidade.

### stage_063_demo_approval

- Route ID: `route_84e3e3cff93a1a32`
- Decisao humana: `APPROVE`
- Status humano: `APPROVED`
- Tipo de rota: `SUPERVISED_CONTINUATION`
- Proxima acao: `ALLOW_INTERNAL_SUPERVISED_CONTINUATION`
- Artefato: `reports/supervised_continuation_queue/stage_064_stage_063_demo_approval_continuation.json`

A decisao humana aprovou continuidade interna supervisionada. Publicacao e deploy seguem bloqueados.

### stage_063_demo_denial

- Route ID: `route_17707c34ece6a9e4`
- Decisao humana: `DENY`
- Status humano: `DENIED`
- Tipo de rota: `EXECUTION_BLOCK`
- Proxima acao: `BLOCK_EXECUTION`
- Artefato: `reports/decision_blocks/stage_064_stage_063_demo_denial_block.json`

A decisao humana negou o pacote. Qualquer continuidade automatica deve ser bloqueada.

### stage_064_router_demo_adjustments

- Route ID: `route_2ee236ae9f71aeb7`
- Decisao humana: `REQUEST_ADJUSTMENTS`
- Status humano: `ADJUSTMENTS_REQUESTED`
- Tipo de rota: `PLANNER_REVISION_REQUEST`
- Proxima acao: `REQUEST_PLANNER_ADJUSTMENTS`
- Artefato: `reports/planning_adjustment_requests/stage_064_stage_064_router_demo_adjustments_adjustment_request.json`

A decisao humana pediu ajustes. O pacote deve voltar ao planejador antes de qualquer continuidade.

### stage_064_router_demo_approve

- Route ID: `route_bb22d7a3424fa1f9`
- Decisao humana: `APPROVE`
- Status humano: `APPROVED`
- Tipo de rota: `SUPERVISED_CONTINUATION`
- Proxima acao: `ALLOW_INTERNAL_SUPERVISED_CONTINUATION`
- Artefato: `reports/supervised_continuation_queue/stage_064_stage_064_router_demo_approve_continuation.json`

A decisao humana aprovou continuidade interna supervisionada. Publicacao e deploy seguem bloqueados.

### stage_064_router_demo_deny

- Route ID: `route_e635fe3c8a84f83f`
- Decisao humana: `DENY`
- Status humano: `DENIED`
- Tipo de rota: `EXECUTION_BLOCK`
- Proxima acao: `BLOCK_EXECUTION`
- Artefato: `reports/decision_blocks/stage_064_stage_064_router_demo_deny_block.json`

A decisao humana negou o pacote. Qualquer continuidade automatica deve ser bloqueada.

## Travas confirmadas

- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem navegador automatico
- Sem mouse automatico
- Continuidade somente supervisionada
