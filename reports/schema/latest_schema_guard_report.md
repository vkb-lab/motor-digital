# K-OS Schema Guard Report

- Checkpoint: 016
- Module: k_os_schema_guard
- Status: blocked_by_schema
- OK: False
- Generated at: 2026-05-31T11:53:33+00:00
- Errors: 11
- Blocking errors: 11

## Results

- content_packs/marketplace_ia/instagram_posts.json | schema=instagram_posts_v1 | ok=True | errors=0
- content_packs/marketplace_ia/instagram_posts_v2.json | schema=instagram_posts_v1 | ok=True | errors=0
- live/marketplace_ia/lead_intake.jsonl | schema=auto_jsonl | ok=True | errors=0
- live/marketplace_ia/public_capture_queue.jsonl | schema=auto_jsonl | ok=True | errors=0
- live/marketplace_ia/latest_lead_diagnostic.json | schema=diagnostic_v1 | ok=True | errors=0
- live/marketplace_ia/latest_public_lead_diagnostic.json | schema=diagnostic_v1 | ok=True | errors=0
- live/marketplace_ia/latest_commercial_proposal.json | schema=proposal_v1 | ok=True | errors=0
- live/marketplace_ia/latest_public_commercial_proposal.json | schema=proposal_v1 | ok=True | errors=0
- live/marketplace_ia/instagram_approval_decision.json | schema=gate_decision_v1 | ok=False | errors=1
- live/marketplace_ia/proposal_approval_decision.json | schema=proposal_v1 | ok=False | errors=5
- live/marketplace_ia/public_proposal_approval_decision.json | schema=proposal_v1 | ok=False | errors=5