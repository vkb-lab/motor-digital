# K-OS Sales Pipeline and Deal Desk

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T16:33:33+00:00
- Pipeline committed: False
- External send enabled: False
- Automatic close enabled: False

## Pipeline

- deal_count: 1
- open_deal_count: 1
- won_count: 0
- lost_count: 0
- stage_counts: {'proposal_draft': 1}
- priority_counts: {'medium': 1}
- open_mrr_estimate_brl: 997.0
- weighted_mrr_estimate_brl: 348.95
- open_setup_estimate_brl: 1500.0
- weighted_arr_estimate_brl: 4187.4

## Deals

- deal_3ea6bff3bf5e | demo_customer | proposal_draft | MRR=997.0 | prob=35% | next=revisar proposta demo e validar ordem comercial

## Required gates before marking active

- crm_customer_exists
- commercial_order_form
- legal_review_if_paid
- commercial_owner_approval
- billing_subscription_active
- license_gate_active
- ai_risk_classifier
- agent_permission_matrix
- human_operator_approval

## Blocked actions

- activate_customer_from_deal_without_approval
- send_proposal_externally_without_gate
- mark_won_without_commercial_approval
- mark_active_without_subscription
- mark_active_without_license_gate
- commit_raw_customer_data
- delete_deal_audit_logs

## Next checkpoint

- 029 - K-Proposal Factory and Quote Builder