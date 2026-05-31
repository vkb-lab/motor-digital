# K-OS Customer Registry and CRM Core

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T16:27:25+00:00
- Registry committed: False
- External send enabled: False
- Automatic message enabled: False

## Pipeline

- customer_count: 1
- open_pipeline_count: 1
- status_counts: {'trial': 1}
- active_customer_count: 0
- trial_count: 1
- past_due_count: 0
- suspended_count: 0

## Customers

- cus_85220a57e183 | demo_customer | trial | agent=marketplace_ia_agent

## Required gates before customer activation

- crm_customer_exists
- billing_subscription_active
- license_gate_active
- commercial_order_form
- ai_risk_classifier
- agent_permission_matrix
- human_operator_approval

## Blocked actions

- commit_raw_customer_contacts
- external_message_without_approval
- automatic_whatsapp_without_gate
- automatic_email_without_gate
- customer_data_delete_without_policy
- audit_log_delete
- activate_customer_without_subscription_or_license

## Next checkpoint

- 028 - K-Sales Pipeline and Deal Desk