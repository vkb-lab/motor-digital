# K-Atlas Stage 64 - Bootstrap Report

Modulo criado: Decision Flow Router

Objetivo:
- APPROVE permite continuidade interna supervisionada
- DENY bloqueia execucao
- REQUEST_ADJUSTMENTS devolve ao planejador para revisao

Arquivos principais:
- agents/decision_flow_router.py
- pages/64_Decision_Flow_Router.py
- ops/run_decision_flow_router_demo.ps1
- live/decision_flow_router/routed_decisions.json
- live/decision_flow_router/approved_continuation_queue.json
- live/decision_flow_router/blocked_denied_queue.json
- live/decision_flow_router/adjustment_request_queue.json
- live/supervised_continuation_queue/stage_064_supervised_continuation_queue.json
- memory/decision_flow_router/routes.jsonl
- memory/decision_flow_router/events.jsonl
- reports/decision_flow_router/stage_064_smoke_report.md
- reports/decision_flow_router/stage_065_next_prompt.md

Governanca:
- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem navegador automatico
- Sem mouse automatico
- Continuidade somente supervisionada

Gerado em: 2026-05-30 02:13:52
