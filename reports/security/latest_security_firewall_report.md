# K-OS Security Firewall Report

- Status: blocked
- OK: False
- Generated at: 2026-05-31T00:00:53.274504+00:00
- Files scanned: 3719
- Findings: 34
- Blocking findings: 34

## Findings

- high | blocked_path_fragment | README_CREDENTIAL_VAULT.md | path contains credential
- high | blocked_path_fragment | content_packs/marketplace_ia/manual_send_pack_template.md | path contains manual_send_pack
- high | blocked_path_fragment | k_atlas/browser/instagram_profile/Default/Network/Trust Tokens | path contains token
- high | blocked_path_fragment | k_atlas/browser/instagram_profile/Default/Network/Trust Tokens-journal | path contains token
- critical | blocked_extension | k_atlas/browser/instagram_profile/Default/heavy_ad_intervention_opt_out.db | extension .db is blocked
- critical | blocked_extension | k_atlas/browser/instagram_profile/first_party_sets.db | extension .db is blocked
- high | blocked_path_fragment | k_atlas/core/credential_vault/__init__.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/credential_vault/env_contract.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/credential_vault/policy.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/credential_vault/smoke_test_credential_vault.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/credential_vault/vault.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/external_live_credential_check/__init__.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/external_live_credential_check/core.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/external_live_credential_check/smoke_test_external_live_credential_check.py | path contains credential
- high | blocked_path_fragment | k_atlas/core/external_token_policy/__init__.py | path contains token
- high | blocked_path_fragment | k_atlas/core/external_token_policy/core.py | path contains token
- high | blocked_path_fragment | k_atlas/core/external_token_policy/smoke_test_external_token_policy.py | path contains token
- high | blocked_path_fragment | k_atlas/core/secrets_manager.py | path contains secret
- high | blocked_path_fragment | k_atlas/security/credential_vault/__init__.py | path contains credential
- high | blocked_path_fragment | k_atlas/security/credential_vault/vault.py | path contains credential
- critical | blocked_path_prefix | live/decision_flow_router/adjustment_request_queue.json | path starts with live/
- critical | blocked_path_prefix | live/decision_flow_router/approved_continuation_queue.json | path starts with live/
- critical | blocked_path_prefix | live/decision_flow_router/blocked_denied_queue.json | path starts with live/
- critical | blocked_path_prefix | live/decision_flow_router/latest_route_state.json | path starts with live/
- critical | blocked_path_prefix | live/decision_flow_router/routed_decisions.json | path starts with live/
- critical | blocked_path_prefix | live/executor_package_builder/executor_package_queue.json | path starts with live/
- critical | blocked_path_prefix | live/executor_package_builder/latest_executor_package_state.json | path starts with live/
- critical | blocked_path_prefix | live/human_decision_center/decision_queue.json | path starts with live/
- critical | blocked_path_prefix | live/human_decision_center/latest_decision_state.json | path starts with live/
- critical | blocked_path_prefix | live/supervised_continuation_queue/stage_064_supervised_continuation_queue.json | path starts with live/
- high | blocked_path_fragment | ops/check_credential_vault.ps1 | path contains credential
- high | blocked_path_fragment | pages/16_K_Atlas_Credential_Vault.py | path contains credential
- high | blocked_path_fragment | pages/250_K_Atlas_ExternalTokenPolicy.py | path contains token
- high | blocked_path_fragment | pages/269_K_Atlas_ExternalLiveCredentialCheck.py | path contains credential