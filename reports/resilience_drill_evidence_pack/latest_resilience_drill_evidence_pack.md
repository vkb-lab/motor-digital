# K-OS Resilience Drill Evidence Pack

- Pack ID: rdep_fb05dd6f9160
- Status: evidence_pack_ready_with_followup
- Evidence complete: True
- Required evidence: 11/11
- Evidence pack hash: a2c3248a616ff9e274d59c2d7b76ff13a0f1fe7bd03a71677850176433659355
- Evidence chain hash: 064829cc53c488d0491300284e96e3359eec48b67c27134f705fdeca8bf00b5f
- Executes drill: False
- Executes recovery: False
- Executes rollback: False
- Executes shell: False

## Evidence items

- operator_review | required=True | available=True | status=operator_review_requires_followup | hash=b4d611104d0b6a413cae41bba3835528bb39b1af43e0de2b8709455152f7db43
- operator_review_report | required=False | available=True | status=audit_generated | hash=832a2def0769b127c013e4da119f3830ac21a02c3dd1b81109795a6bcee929dc
- operator_review_validation | required=True | available=True | status=validated | hash=943792742cc5d2e64d5a9769c90337bdaaf0510fcdc60d4374e5d524092b5b40
- drill_dry_run | required=True | available=True | status=dry_run_completed_safe | hash=d241832f62320c1fac9b9144095f71f9c9cf2fdeed76f98004cf22653aa47605
- drill_dry_run_validation | required=True | available=True | status=validated | hash=94478ef7536ff30140e2988250657aa331f5e43663873802fd882364bb0cd449
- drill_design | required=True | available=True | status=drills_designed | hash=71f7332d7887157792c55c07ef87cc986d4b15a9d9ebe3eb648989aaa6db6bfe
- drill_design_validation | required=True | available=True | status=validated | hash=8201e3d3af6c287a9a7d079a4ddc40051d47e765a6f93a77efbb8aea9f6399a1
- scenario_plan | required=True | available=True | status=scenarios_review_required | hash=caa21d49f68a06bd6c8196d348024b0ca0aad0cd9e57c8990f83e82fbed77867
- scenario_validation | required=True | available=True | status=validated | hash=3d96c1d0a14a5afb902344805decd9b00b4b021b5f28a1bbfdf6e9f5c9ec3f25
- readiness_matrix | required=True | available=True | status=resilience_blocked | hash=c0a79c80d7c05e89116da9034e78172fd44ef6b019aa31d1226b95b0be62e30f
- readiness_validation | required=True | available=True | status=validated | hash=742dcad9954c71db89c29e03d07ec038415b5ef3f36f77b6f17f04e87ad82735
- recovery_layer_closure | required=True | available=True | status=layer_blocked | hash=887114ae713444be76f00362854217ef75dcc14f206b7bd2d3e2496675ba3fce

## Blockers

- Nenhum blocker.

## Warnings

- operator_review_not_clean_recorded
- scenario_plan_not_clean_planned

## Followups

- carry_operator_review_followup_to_governance_summary_077
- carry_scenario_followup_to_governance_summary_077