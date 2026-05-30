# K-Atlas Central Report

Generated at: 2026-05-30T00:15:25.663677+00:00
Checkpoint: 37 - AutoReporter Central

## Status

- Current autonomy level: level_3_assisted_execution
- Next target: level_4_limited_real_publish_after_vault_api_and_approval
- Modules OK: 10 / 10
- Streamlit pages: 11
- Control Plane events: 0
- Supervisor queue items: 0

## Modules

- control_plane: True
- workflows: True
- blackboard: True
- supervisor_autopilot: True
- credential_vault: True
- sandbox_api_adapter: True
- creative_media_gateway: True
- saas_builder: True
- social_audit: True
- publishing_gateway: True

## Guardrails

- sem publicação oficial automática
- sem token em texto puro
- sem browser automation para conta oficial
- sem mensagem em massa
- human review obrigatório para risco médio/alto

## Git

- Branch: main

### Last commits

```text
df5bea6 feat: add sandbox api adapter
a20e790 feat: add credential vault governance
f078fa1 feat: add supervisor autopilot
3c996cf feat: add saas builder agent bridge
4b5ac31 feat: add creative media gateway
7c41a9f feat: add k atlas official instagram plan
d8b3ce9 feat: add k atlas autonomy ladder runner
a19fbc5 fix: stabilize agent workflows autonomy smoke test
13bb5d4 fix: stabilize agent workflows autonomy smoke test
6982cad feat: add social audit live mode
```

### Status

```text
M k_atlas/social/memory/campaign_package_approval_queue.json
 M k_atlas/social/memory/social_approval_queue.json
 M k_atlas/social/memory/social_content_refinement_queue.json
 M k_atlas/social/reports/campaign_packages/campaign_package_index.json
 M k_atlas/social/reports/social_command_center.json
?? .checkpoint_37_autoreporter.py
?? README_AUTOREPORTER_CENTRAL.md
?? k_atlas/core/autoreporter/
?? memory/sandbox_api_adapter/
?? ops/run_autoreporter_central.ps1
?? pages/18_K_Atlas_AutoReporter_Central.py
```

## Next checkpoints

- 38 - SaaS Factory workflow real
- 39 - Deploy pipeline assistido
- 40 - K-Atlas Assisted Autonomy v1