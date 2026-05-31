# K-OS Support Desk and Ticketing Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T18:35:40+00:00
- Registry committed: False
- External send enabled: False
- Automatic message enabled: False

## Metrics

- ticket_count: 1
- open_ticket_count: 1
- critical_ticket_count: 0
- high_ticket_count: 0
- sla_at_risk_count: 0
- sla_breached_count: 0
- status_counts: {'new': 1}
- priority_counts: {'medium': 1}
- category_counts: {'delivery': 1}
- sla_counts: {'ok': 1}

## Tickets

- tkt_c45e3d6002a2 | demo_customer | delivery | medium | new | sla=ok

## Required gates before ticket close

- ticket_exists
- operator_review
- customer_success_review_if_delivery_related
- commercial_review_if_billing_or_license_related
- incident_review_if_security_or_data_related
- audit_event_recorded

## Blocked actions

- send_customer_reply_without_approval
- publish_ticket_externally
- commit_raw_ticket_notes
- delete_support_audit_logs
- close_critical_ticket_without_review
- ignore_security_or_data_incident
- expose_customer_contact_in_report

## Next checkpoint

- 033 - K-Knowledge Base and Support Playbooks