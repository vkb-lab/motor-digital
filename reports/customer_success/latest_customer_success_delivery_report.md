# K-OS Customer Success and Delivery Tracker

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T18:29:03+00:00
- Registry committed: False
- External send enabled: False
- Automatic message enabled: False

## Metrics

- account_count: 1
- delivery_count: 1
- task_count: 5
- open_task_count: 5
- high_risk_count: 0
- red_health_count: 0
- health_counts: {'yellow': 1}
- risk_counts: {'medium': 1}
- delivery_counts: {'planned': 1}
- task_counts: {'todo': 5}

## Accounts

- csa_35f68b36bf98 | demo_customer | health=yellow | risk=medium | next=revisar onboarding e confirmar primeira entrega

## Open Tasks

- tsk_47eda852167b | demo_customer | Confirmar escopo de onboarding | todo
- tsk_f76d7f95dea0 | demo_customer | Validar permissões do agente | todo
- tsk_ed4c42b7f4d6 | demo_customer | Revisar pacote de proposta e assinatura | todo
- tsk_5cffbd810a88 | demo_customer | Definir rotina de acompanhamento | todo
- tsk_6bc130abf23f | demo_customer | Registrar critério de sucesso do cliente | todo

## Required gates before delivery completion

- customer_success_account_exists
- delivery_items_reviewed
- operator_review
- customer_acceptance_if_required
- commercial_review_if_risk_high
- audit_event_recorded

## Blocked actions

- send_customer_message_without_approval
- publish_customer_update_externally
- mark_delivery_complete_without_review
- delete_customer_success_audit_logs
- commit_raw_customer_notes
- ignore_high_churn_risk

## Next checkpoint

- 032 - K-Support Desk and Ticketing Core