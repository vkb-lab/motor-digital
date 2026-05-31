# K-OS Knowledge Base and Support Playbooks

- Status: audit_generated
- OK: True
- Generated at: 2026-05-31T19:22:34+00:00
- Registry committed: False
- External send enabled: False
- External publish enabled: False

## Metrics

- article_count: 1
- playbook_count: 1
- template_count: 1
- ticket_link_count: 1
- article_status_counts: {'draft': 1}
- playbook_status_counts: {'draft': 1}
- category_counts: {'delivery': 2}

## Articles

- kb_88e483f385d6 | Como validar primeira entrega K-OS | delivery | draft

## Playbooks

- pb_3b663a5dbf29 | Playbook de triagem de ticket de delivery | delivery | draft | steps=7

## Response templates

- tpl_deedf3fe1a05 | Resposta interna para atualização de entrega | approval=True

## Required gates before customer-facing use

- article_or_playbook_exists
- operator_review
- support_owner_review
- security_review_if_security_related
- legal_review_if_legal_or_commercial_related
- customer_data_sanitized
- approval_event_recorded

## Blocked actions

- send_response_without_approval
- publish_article_externally
- commit_raw_customer_examples
- delete_knowledge_audit_logs
- use_legal_template_without_review
- use_security_playbook_without_security_review
- expose_customer_contact_in_article

## Next checkpoint

- 034 - K-Product Feedback and Feature Request Core