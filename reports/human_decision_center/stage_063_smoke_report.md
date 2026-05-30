# K-Atlas Stage 63 - Human Decision Center Smoke Report

Status: `PASS`
Gerado em: 2026-05-30T05:01:06+00:00

## Resultado

- Pacotes demo criados: 3
- Decisoes registradas: 3
- Fila antes: {"total_packages": 4, "pending_decisions": 4, "decided_packages": 0}
- Fila depois: {"total_packages": 4, "pending_decisions": 1, "decided_packages": 3}

## Decisoes testadas

- `stage_063_demo_approval` -> `APPROVE` -> `APPROVED`
- `stage_063_demo_denial` -> `DENY` -> `DENIED`
- `stage_063_demo_adjustments` -> `REQUEST_ADJUSTMENTS` -> `ADJUSTMENTS_REQUESTED`

## Artefatos

- queue: `live/human_decision_center/decision_queue.json`
- decisions_jsonl: `memory/human_decision_center/decisions.jsonl`
- events_jsonl: `memory/human_decision_center/events.jsonl`
- latest_state: `live/human_decision_center/latest_decision_state.json`
- queue_report: `reports/human_decision_center/stage_063_decision_queue_report.md`
- next_prompt: `reports/human_decision_center/stage_064_next_prompt.md`

## Travas confirmadas

- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem navegador automatico
- Sem mouse automatico
