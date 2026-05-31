# K-OS Billing and Subscription Ledger

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T16:23:32+00:00
- Ledger committed: False
- Real charge enabled: False
- Manual payment status only: True

## Metrics

- subscription_count: 1
- active_count: 0
- trial_count: 1
- past_due_count: 0
- suspended_count: 0
- expired_count: 0
- mrr_estimate_brl: 0.0
- arr_estimate_brl: 0.0

## Subscriptions

- sub_5eb90805e732 | demo_customer | marketplace_ia_agent | trial_7d | trial

## Required gates before paid activation

- commercial_order_form
- legal_review_if_required
- billing_subscription_active
- license_gate_active
- ai_risk_classifier
- agent_permission_matrix
- human_operator_approval

## Blocked actions

- real_charge_without_processor_policy
- tax_invoice_without_accounting_review
- activate_agent_without_license_gate
- activate_agent_without_active_subscription
- silent_customer_data_wipe
- delete_billing_audit_logs
- external_payment_api_call_without_sandbox

## Next checkpoint

- 027 - K-Customer Registry and CRM Core