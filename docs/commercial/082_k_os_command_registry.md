# 082 - K-OS Command Registry Core

Gerado em: 2026-06-01T13:10:21Z

## Objetivo

Criar registro central de comandos do K-OS com catalogo local, classificacao de risco, politica de execucao, evidencias sanitizadas e dashboard somente leitura, sem executar comandos, agentes, modulos, auto-fix, recovery, rollback, drill, reset ou force push.

## Status

- Checkpoint: 082
- Camada: K-OS Core
- Status do registry: healthy
- Checkpoint anterior: 081 - K-OS Agent Capability Registry Core
- Proximo checkpoint: 083 - K-OS Backup and Export Pack Core
- Superficies de comando registradas: 1579
- Revisao de operador requerida: 200
- Referencias bloqueadas detectadas: 3

## Contagem por familia

| Familia | Quantidade |
|---|---:|
| audit | 21 |
| closure | 24 |
| configuration | 34 |
| documentation | 32 |
| git_workflow | 425 |
| powershell_wrapper | 24 |
| python_runtime | 88 |
| registry_generation | 20 |
| report_generation | 159 |
| security_guard | 152 |
| streamlit_runtime | 520 |
| validation | 80 |

## Contagem por risco

| Risco | Quantidade |
|---|---:|
| blocked_reference | 3 |
| git_publish | 188 |
| operator_review_required | 9 |
| read_only | 1348 |
| write_artifact | 31 |

## Contagem por raiz

| Raiz | Quantidade |
|---|---:|
| configs | 6 |
| docs | 65 |
| k_atlas | 6 |
| pages | 569 |
| reports | 924 |
| scripts | 9 |

## Raizes monitoradas

| Raiz | Existe | Status | Superficies |
|---|---|---|---:|
| scripts | True | found | 9 |
| k_atlas | True | found | 6 |
| pages | True | found | 569 |
| configs | True | found | 6 |
| docs | True | found | 65 |
| reports | True | found | 924 |

## Familias obrigatorias ausentes

Nenhuma familia obrigatoria ausente.

## Revisao de operador

| Caminho | Familia | Risco |
|---|---|---|
| scripts/aprovar.ps1 | python_runtime | operator_review_required |
| scripts/atlas.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_077_resilience_governance_summary.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_078_resilience_layer_closure.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_079_system_health_monitor.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_080_module_registry.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_081_agent_capability_registry.ps1 | powershell_wrapper | operator_review_required |
| scripts/checkpoint_082_command_registry.ps1 | powershell_wrapper | operator_review_required |
| scripts/navegar.ps1 | python_runtime | operator_review_required |
| k_atlas/ops/command_registry_082.py | git_workflow | git_publish |
| reports/assisted_autonomy/2cb348aa-d11a-4122-9a90-59ca24722179.json | git_workflow | git_publish |
| reports/assisted_autonomy/deploy_pipeline/85c3989e-1b31-49ad-ade6-a49751c18073.json | git_workflow | git_publish |
| reports/assisted_autonomy/deploy_pipeline/latest_deploy_pipeline_report.json | git_workflow | git_publish |
| reports/assisted_autonomy/k_atlas_assisted_autonomy_v1.json | git_workflow | git_publish |
| reports/command_center/latest_command_center_run.json | git_workflow | git_publish |
| reports/cowork_pilot_studio/latest_cowork_pilot_studio.json | powershell_wrapper | blocked_reference |
| reports/daily_operator/latest_daily_operator_cockpit.json | git_workflow | git_publish |
| reports/deploy_pipeline/017f4254-5f31-4b45-a992-b6d2c60ae5f9.json | git_workflow | git_publish |
| reports/deploy_pipeline/01941d36-6322-41a9-b220-e026331927ee.json | git_workflow | git_publish |
| reports/deploy_pipeline/01cd8c03-04c5-4f50-8ee3-bce1477f3e0f.json | git_workflow | git_publish |
| reports/deploy_pipeline/0251f30d-59f1-430c-8570-99f578b18c86.json | git_workflow | git_publish |
| reports/deploy_pipeline/02d85f23-5df1-4ff6-bfd5-162b7019004e.json | git_workflow | git_publish |
| reports/deploy_pipeline/059eed8f-31c3-4f00-bdd9-e0b2f2898cae.json | git_workflow | git_publish |
| reports/deploy_pipeline/06cfd3c8-7108-4710-be14-1d819fc2175c.json | git_workflow | git_publish |
| reports/deploy_pipeline/0b982b6f-e20c-4370-bc09-8c51403d7b8f.json | git_workflow | git_publish |
| reports/deploy_pipeline/0c0b6a48-ffe5-45d7-8c37-5f6df4318aae.json | git_workflow | git_publish |
| reports/deploy_pipeline/0ec5d461-a090-448b-89cf-d9207e37c002.json | git_workflow | git_publish |
| reports/deploy_pipeline/12c0a9c7-f5dd-4a39-8968-14b14f66d8e1.json | git_workflow | git_publish |
| reports/deploy_pipeline/13af7cb9-2eb1-465c-b518-7d3fe36ac450.json | git_workflow | git_publish |
| reports/deploy_pipeline/13f07057-e75e-4094-b621-729e8a539532.json | git_workflow | git_publish |
| reports/deploy_pipeline/1465da39-ccd6-4336-8219-7d25c8e5bb7b.json | git_workflow | git_publish |
| reports/deploy_pipeline/16b56997-1568-4a66-9888-6f47dd00aac9.json | git_workflow | git_publish |
| reports/deploy_pipeline/17270bda-96e9-46ed-b400-f0c7acb1ad5d.json | git_workflow | git_publish |
| reports/deploy_pipeline/1727ec17-84af-4fbd-b242-927c058c6c3d.json | git_workflow | git_publish |
| reports/deploy_pipeline/19e07e7b-8406-42df-b035-cd5d5d276edd.json | git_workflow | git_publish |
| reports/deploy_pipeline/1b635829-dc1c-432d-9a23-ead6dbd05c39.json | git_workflow | git_publish |
| reports/deploy_pipeline/1c8ccf81-6f65-4de9-96c9-ef716eeb75ae.json | git_workflow | git_publish |
| reports/deploy_pipeline/2005941d-e073-4ef4-bce0-e73e36519b11.json | git_workflow | git_publish |
| reports/deploy_pipeline/2042c33f-dab5-41f2-bdcd-b0196259f1ba.json | git_workflow | git_publish |
| reports/deploy_pipeline/20f61d96-d217-4600-9f5a-bfe373448300.json | git_workflow | git_publish |
| reports/deploy_pipeline/21215431-57c2-4fcc-9bf4-b3dbb313f299.json | git_workflow | git_publish |
| reports/deploy_pipeline/23bb258f-2155-4b15-8e25-6afb2e8c492b.json | git_workflow | git_publish |
| reports/deploy_pipeline/24a23688-2924-4ab5-aef5-17e6f5a17d50.json | git_workflow | git_publish |
| reports/deploy_pipeline/2682243d-57e0-446f-9c71-95305425f039.json | git_workflow | git_publish |
| reports/deploy_pipeline/28f08953-9041-43e1-a933-c893959da9b0.json | git_workflow | git_publish |
| reports/deploy_pipeline/2a12bf34-906f-474e-821e-a4b990538c81.json | git_workflow | git_publish |
| reports/deploy_pipeline/2a241fd4-6447-401e-93c2-d3e9485af9e3.json | git_workflow | git_publish |
| reports/deploy_pipeline/2c7f72e8-5abd-44ef-a27e-6f3b622d52e0.json | git_workflow | git_publish |
| reports/deploy_pipeline/2d64ed06-c873-4ce8-be24-02c51fc47e8a.json | git_workflow | git_publish |
| reports/deploy_pipeline/300c5410-2627-4e41-9033-d73e968bf82c.json | git_workflow | git_publish |
| reports/deploy_pipeline/30d28272-f83f-4f96-a42f-2d016e74058d.json | git_workflow | git_publish |
| reports/deploy_pipeline/31b0fa36-d41a-46b8-b5e2-801383d6e5ee.json | git_workflow | git_publish |
| reports/deploy_pipeline/31eee43d-c72d-4269-900f-8d2f34938393.json | git_workflow | git_publish |
| reports/deploy_pipeline/33be26fe-19a9-4976-afc6-7cbf73742f62.json | git_workflow | git_publish |
| reports/deploy_pipeline/3566d88e-9ec4-4378-a533-aecf46b8a7f1.json | git_workflow | git_publish |
| reports/deploy_pipeline/3596584d-91f2-4188-865e-331618cf104c.json | git_workflow | git_publish |
| reports/deploy_pipeline/369a5eed-0d34-4496-9896-2014f0b12c3f.json | git_workflow | git_publish |
| reports/deploy_pipeline/36acc132-d8dc-4460-a536-a3de4c332c11.json | git_workflow | git_publish |
| reports/deploy_pipeline/37e8ebfa-2995-4b64-80d1-224ef1efada2.json | git_workflow | git_publish |
| reports/deploy_pipeline/383b42c7-79ab-424d-9e05-49c8279f2274.json | git_workflow | git_publish |
| reports/deploy_pipeline/387b9944-669a-46ab-822f-5ae040647af3.json | git_workflow | git_publish |
| reports/deploy_pipeline/38970483-1d3d-4328-88d1-ec6e68c32db7.json | git_workflow | git_publish |
| reports/deploy_pipeline/3b8eb3f2-49ee-4030-ad0a-1fa7cf1e8ae8.json | git_workflow | git_publish |
| reports/deploy_pipeline/3b929ba4-6c3b-46e1-aa49-e5b1090c0e4b.json | git_workflow | git_publish |
| reports/deploy_pipeline/3ccedea1-eca2-481e-bc5d-5b279318098e.json | git_workflow | git_publish |
| reports/deploy_pipeline/3cfe5ff6-adb2-4377-aee4-cbaa2f235db4.json | git_workflow | git_publish |
| reports/deploy_pipeline/42635f9a-30e7-4f02-bab7-7a1ede603786.json | git_workflow | git_publish |
| reports/deploy_pipeline/454c1c92-91e8-4c12-a088-a670ddaefcb4.json | git_workflow | git_publish |
| reports/deploy_pipeline/464b09dc-54e8-4f96-abd0-2451c14ec42f.json | git_workflow | git_publish |
| reports/deploy_pipeline/46715277-b9d9-4c2d-ad7d-3d834dd216bd.json | git_workflow | git_publish |
| reports/deploy_pipeline/4687775b-ceea-4536-9f97-8a57537117c4.json | git_workflow | git_publish |
| reports/deploy_pipeline/4687d57a-16bd-4c21-ab7f-afb7c3118b56.json | git_workflow | git_publish |
| reports/deploy_pipeline/47ee14bb-0d28-422a-9e43-8883f8a7fc8a.json | git_workflow | git_publish |
| reports/deploy_pipeline/49830645-700e-4677-90d5-e356f2d127b5.json | git_workflow | git_publish |
| reports/deploy_pipeline/4c287aac-35be-4a64-b115-173b7ec44e13.json | git_workflow | git_publish |
| reports/deploy_pipeline/4e9a8888-c931-455f-83c1-0c0a2937a372.json | git_workflow | git_publish |
| reports/deploy_pipeline/4feb5915-1719-45b6-b93a-2a4c75fcf474.json | git_workflow | git_publish |
| reports/deploy_pipeline/5004ce15-6084-4311-aed6-71911b9b4500.json | git_workflow | git_publish |
| reports/deploy_pipeline/5060069e-bb91-43fc-b1a9-f6b9e7fde241.json | git_workflow | git_publish |
| reports/deploy_pipeline/52b30cb2-c1c5-4c51-be86-3769a67fdebd.json | git_workflow | git_publish |

## Amostra de comandos registrados

| Familia | Risco | Caminho | Politica |
|---|---|---|---|
| python_runtime | operator_review_required | scripts/aprovar.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/atlas.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_077_resilience_governance_summary.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_078_resilience_layer_closure.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_079_system_health_monitor.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_080_module_registry.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_081_agent_capability_registry.ps1 | read_only_registered_not_executed |
| powershell_wrapper | operator_review_required | scripts/checkpoint_082_command_registry.ps1 | read_only_registered_not_executed |
| python_runtime | operator_review_required | scripts/navegar.ps1 | read_only_registered_not_executed |
| security_guard | write_artifact | k_atlas/ops/agent_capability_registry_081.py | read_only_registered_not_executed |
| git_workflow | git_publish | k_atlas/ops/command_registry_082.py | read_only_registered_not_executed |
| security_guard | write_artifact | k_atlas/ops/module_registry_080.py | read_only_registered_not_executed |
| security_guard | write_artifact | k_atlas/ops/resilience_governance_summary_077.py | read_only_registered_not_executed |
| security_guard | write_artifact | k_atlas/ops/resilience_layer_closure_078.py | read_only_registered_not_executed |
| security_guard | write_artifact | k_atlas/ops/system_health_monitor_079.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/077_Resilience_Governance_Summary.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/078_Resilience_Layer_Closure.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/079_K_OS_System_Health_Monitor.py | read_only_registered_not_executed |
| python_runtime | read_only | pages/07_K_Social_Publishing_Gateway.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/080_K_OS_Module_Registry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/081_K_OS_Agent_Capability_Registry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/082_K_OS_Command_Registry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/08_Etapa_7_Independencia.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/09_K_Atlas_Control_Plane.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/100_K_Atlas_Local_OS_Release_Capsule.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/101_K_Atlas_Local_OS_Health_Check.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/102_K_Atlas_Startup_Manager.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/103_K_Atlas_One_Click_Launcher.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/104_K_Atlas_Operator_Home.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/105_K_Atlas_MVP_Validation_Report.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/106_K_Atlas_Download_Intake_UX.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/113_K_Atlas_Update_Intake_Queue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/114_K_Atlas_Update_Verification_Gate.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/115_K_Atlas_Update_Apply_Runner.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/116_K_Atlas_Update_Rollback_Hook.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/117_K_Atlas_Update_Pipeline_Dashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/118_K_Atlas_Silent_Update_Status_Center.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/119_K_Atlas_Auto_Update_Notification_Bridge.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/11_K_Atlas_Lousa_Operacional.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/120_K_Atlas_Download_Cleanup_Policy.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/121_K_Atlas_Operator_Clipboard_Return.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/122_K_Atlas_Auto_Update_UX_Dashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/123_K_Atlas_Principal_Shell_Cover.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/12_K_Atlas_Social_Audit_Local.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/133_K_Atlas_Local_OS_Brain_Governance.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/134_K_Atlas_AgentRuntimeRegistry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/135_K_Atlas_AgentTaskIntake.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/136_K_Atlas_AgentBrainAuthorizationBridge.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/137_K_Atlas_AgentExecutionSandbox.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/138_K_Atlas_AgentRuntimeDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/139_K_Atlas_AgentResultEvaluator.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/13_K_Atlas_Creative_Media_Gateway.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/140_K_Atlas_AgentRetryPolicy.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/141_K_Atlas_AgentEscalationRouter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/142_K_Atlas_AgentRuntimeMemorySync.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/143_K_Atlas_AgentRuntimeControlDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/144_K_Atlas_AgentPerformanceScorer.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/145_K_Atlas_AgentLearningSignalCollector.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/146_K_Atlas_AgentMemoryFeedbackWriter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/147_K_Atlas_AgentImprovementProposalQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/148_K_Atlas_AgentEvolutionDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/149_K_Atlas_AgentSelfReviewEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/14_K_Atlas_SaaS_Builder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/150_K_Atlas_AgentCapabilityRegistry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/151_K_Atlas_AgentSkillGapDetector.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/152_K_Atlas_AgentTrainingMissionQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/153_K_Atlas_AgentTrainingDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/154_K_Atlas_TrainingResultEvaluator.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/155_K_Atlas_TrainingDatasetBuilder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/156_K_Atlas_TrainingReplayQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/157_K_Atlas_TrainingGovernanceGate.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/158_K_Atlas_TrainingControlDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/159_K_Atlas_KnowledgeCaptureEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/15_K_Atlas_Supervisor_Autopilot.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/160_K_Atlas_KnowledgeIndexBuilder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/161_K_Atlas_KnowledgeRetrievalRouter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/162_K_Atlas_KnowledgeFreshnessMonitor.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/163_K_Atlas_KnowledgeControlDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/164_K_Atlas_AgentReasoningTrace.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/165_K_Atlas_AgentDecisionContextBuilder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/166_K_Atlas_AgentRiskClassifier.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/167_K_Atlas_AgentConfidenceScorer.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/168_K_Atlas_AgentReasoningDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/169_K_Atlas_AgentDecisionReviewQueue.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/16_K_Atlas_Credential_Vault.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/170_K_Atlas_AgentDecisionReplayEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/171_K_Atlas_AgentRiskOverrideGate.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/172_K_Atlas_AgentConfidenceCalibration.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/173_K_Atlas_AgentDecisionControlDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/174_K_Atlas_AgentPolicyLearningEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/175_K_Atlas_AgentPolicyDriftMonitor.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/176_K_Atlas_AgentGovernanceFeedbackWriter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/177_K_Atlas_AgentGovernanceMemorySync.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/178_K_Atlas_AgentGovernanceDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/179_K_Atlas_AgentGovernanceReviewQueue.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/17_K_Atlas_Sandbox_API_Adapter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/180_K_Atlas_AgentGovernanceReplayEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/181_K_Atlas_AgentGovernanceExceptionGate.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/182_K_Atlas_AgentGovernanceAuditCapsule.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/183_K_Atlas_AgentGovernanceControlDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/184_K_Atlas_AgentGovernanceHealthCheck.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/185_K_Atlas_AgentGovernanceStartupPolicy.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/186_K_Atlas_AgentGovernanceSnapshotBuilder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/187_K_Atlas_AgentGovernanceRecoveryPlan.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/188_K_Atlas_AgentGovernanceReleaseDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/189_K_Atlas_AgentGovernanceValidationRunner.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/18_K_Atlas_AutoReporter_Central.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/190_K_Atlas_AgentGovernanceComplianceMatrix.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/191_K_Atlas_AgentGovernanceIncidentQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/192_K_Atlas_AgentGovernanceRemediationPlanner.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/193_K_Atlas_AgentGovernanceFinalDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/194_K_Atlas_MultiagentRoleRegistry.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/195_K_Atlas_MultiagentTaskRouter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/196_K_Atlas_MultiagentCollaborationQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/197_K_Atlas_MultiagentConflictResolver.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/198_K_Atlas_MultiagentOrchestrationDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/199_K_Atlas_MultiagentMessageBus.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/19_K_Atlas_SaaS_Factory_Workflow.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/200_K_Atlas_MultiagentSharedMemory.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/201_K_Atlas_MultiagentCoordinationPolicy.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/202_K_Atlas_MultiagentConsensusEngine.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/203_K_Atlas_MultiagentCommandDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/204_K_Atlas_MultiagentExecutionPlanner.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/205_K_Atlas_MultiagentWorkAllocation.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/206_K_Atlas_MultiagentProgressTracker.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/207_K_Atlas_MultiagentResultMerger.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/208_K_Atlas_MultiagentExecutionDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/209_K_Atlas_MultiagentResultValidator.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/20_K_Atlas_Deploy_Pipeline.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/210_K_Atlas_MultiagentQualityScorer.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/211_K_Atlas_MultiagentOutputReviewQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/212_K_Atlas_MultiagentCorrectionPlanner.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/213_K_Atlas_MultiagentQualityDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/214_K_Atlas_MultiagentProductBriefBuilder.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/215_K_Atlas_MultiagentProductTaskSplitter.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/216_K_Atlas_MultiagentProductAssemblyQueue.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/217_K_Atlas_MultiagentProductReviewGate.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/218_K_Atlas_MultiagentProductDashboard.py | read_only_registered_not_executed |
| streamlit_runtime | read_only | pages/219_K_Atlas_MultiagentProductPackagingEngine.py | read_only_registered_not_executed |
| streamlit_runtime | write_artifact | pages/21_K_Atlas_Assisted_Autonomy.py | read_only_registered_not_executed |

## Garantias de nao execucao

- command_execution_performed: False
- agent_execution_performed: False
- module_execution_performed: False
- automatic_remediation_executed: False
- real_drill_executed: False
- real_recovery_executed: False
- real_rollback_executed: False
- git_reset_hard_executed: False
- force_push_executed: False
- destructive_shell_executed: False
- memory_deletion_executed: False
- secret_export_executed: False

## Operacoes bloqueadas

- command_execution
- agent_execution
- module_execution
- automatic_remediation
- real_drill_execution
- real_recovery_execution
- real_rollback_execution
- git_reset_hard
- force_push
- destructive_shell
- memory_deletion
- secret_export

## Decisao operacional

Registro central de comandos criado em modo somente leitura.
O sistema pode seguir para 083 - K-OS Backup and Export Pack Core.
