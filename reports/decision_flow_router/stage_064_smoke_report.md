# K-Atlas Stage 64 - Decision Flow Router Smoke Report

Status: `PASS`
Gerado em: 2026-05-30T05:13:53+00:00

## Validacoes

- approve_routes_to_supervised_continuation: `PASS`
- deny_routes_to_execution_block: `PASS`
- request_adjustments_routes_to_planner_revision: `PASS`
- all_smoke_packages_routed: `PASS`
- approved_queue_file_exists: `PASS`
- denied_queue_file_exists: `PASS`
- adjustment_queue_file_exists: `PASS`
- supervised_queue_file_exists: `PASS`

## Resumo de rotas

- Total de rotas: 6
- Aprovadas: 2
- Negadas/bloqueadas: 2
- Ajustes solicitados: 2

## Artefatos

- routed_decisions: `live/decision_flow_router/routed_decisions.json`
- approved_queue: `live/decision_flow_router/approved_continuation_queue.json`
- denied_queue: `live/decision_flow_router/blocked_denied_queue.json`
- adjustment_queue: `live/decision_flow_router/adjustment_request_queue.json`
- supervised_queue: `live/supervised_continuation_queue/stage_064_supervised_continuation_queue.json`
- route_report: `reports/decision_flow_router/stage_064_route_report.md`
- smoke_report: `reports/decision_flow_router/stage_064_smoke_report.md`
- next_prompt: `reports/decision_flow_router/stage_065_next_prompt.md`

## Travas confirmadas

- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem navegador automatico
- Sem mouse automatico
- Governanca humana mantida
