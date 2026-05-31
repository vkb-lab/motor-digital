# K-OS Proposal Factory and Quote Builder

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T16:40:52+00:00
- Registry committed: False
- External send enabled: False
- Automatic send enabled: False

## Metrics

- proposal_count: 1
- setup_total_brl: 1500.0
- recurring_total_brl: 997.0
- status_counts: {'draft': 1}

## Proposals

- prop_cd60683010d3 | demo_customer | draft | setup=1500.0 | recurring=997.0 | manual_send=False

## Required gates before manual send

- proposal_exists
- deal_exists
- crm_customer_exists
- quote_totals_validated
- commercial_owner_approval
- legal_review_if_paid
- ai_risk_classifier
- human_operator_approval

## Blocked actions

- send_proposal_without_approval
- mark_sent_without_manual_confirmation
- activate_customer_from_proposal
- commit_raw_customer_data
- publish_quote_externally
- guarantee_revenue_claim
- skip_legal_review_for_paid_deal

## Templates

- reports/proposals/templates/proposal_brief_template.md
- reports/proposals/templates/quote_items_template.md
- reports/proposals/templates/manual_send_pack_template.md

## Next checkpoint

- 030 - K-Onboarding and Activation Gate