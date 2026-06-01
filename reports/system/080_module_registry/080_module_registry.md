# 080 - K-OS Module Registry Core

Gerado em: 2026-06-01T12:59:52Z

## Objetivo

Criar registro central de modulos do K-OS com inventario local, classificacao operacional, evidencias sanitizadas e dashboard somente leitura, sem executar modulos, auto-fix, recovery, rollback, drill, reset ou force push.

## Status

- Checkpoint: 080
- Camada: K-OS Core
- Status do registry: healthy
- Checkpoint anterior: 079 - K-OS System Health Monitor Core
- Proximo checkpoint: 081 - K-OS Agent Capability Registry Core
- Total de modulos registrados: 4522

## Contagem por tipo

| Tipo | Quantidade |
|---|---:|
| agent_module | 12 |
| configuration | 290 |
| content_pack | 8 |
| core_python | 1749 |
| documentation | 270 |
| memory_surface | 215 |
| operation_python | 4 |
| report_surface | 916 |
| script_wrapper | 8 |
| streamlit_page | 567 |
| unknown | 483 |

## Contagem por raiz

| Raiz | Quantidade |
|---|---:|
| agents | 12 |
| configs | 5 |
| content_packs | 8 |
| docs | 66 |
| k_atlas | 2664 |
| live | 60 |
| memory | 215 |
| pages | 568 |
| reports | 916 |
| scripts | 8 |

## Raizes monitoradas

| Raiz | Existe | Status | Modulos |
|---|---|---|---:|
| k_atlas | True | found | 2664 |
| agents | True | found | 12 |
| live | True | found | 60 |
| memory | True | found | 215 |
| reports | True | found | 916 |
| campaigns | False | missing | 0 |
| content_packs | True | found | 8 |
| configs | True | found | 5 |
| scripts | True | found | 8 |
| pages | True | found | 568 |
| docs | True | found | 66 |

## Tipos criticos ausentes

Nenhum tipo critico ausente.

## Amostra de modulos registrados

| Tipo | Raiz | Caminho | Status |
|---|---|---|---|
| unknown | k_atlas | k_atlas | registered_directory |
| core_python | k_atlas | k_atlas/__init__.py | registered |
| core_python | k_atlas | k_atlas/agents/commercial_brain.py | registered |
| core_python | k_atlas | k_atlas/agents/commercial_orchestrator.py | registered |
| core_python | k_atlas | k_atlas/agents/decision_engine.py | registered |
| core_python | k_atlas | k_atlas/agents/instagram_content_pack.py | registered |
| core_python | k_atlas | k_atlas/agents/marketing_manager.py | registered |
| core_python | k_atlas | k_atlas/agents/publisher_instagram.py | registered |
| configuration | k_atlas | k_atlas/approved_campaigns/approved_20260528_091253.json | registered |
| unknown | k_atlas | k_atlas/browser/instagram_profile/BrowserMetrics-spare.pma | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Crashpad/settings.dat | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Account Web Data | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Account Web Data-journal | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Affiliation Database | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Affiliation Database-journal | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/AutofillAiModelCache/LOCK | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/AutofillAiModelCache/LOG | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/AutofillStrikeDatabase/LOCK | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/AutofillStrikeDatabase/LOG | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/BookmarkMergedSurfaceOrdering | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/BudgetDatabase/LOCK | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/BudgetDatabase/LOG | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_0 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_1 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_2 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_3 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000001 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000002 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000003 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000004 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000005 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000006 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000007 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000008 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000009 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000e | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000f | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000010 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000011 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000012 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000013 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000014 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000015 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000016 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000017 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000018 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000019 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001e | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001f | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000020 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000021 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000022 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000023 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000024 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000025 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000026 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000027 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000028 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000029 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002e | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002f | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000030 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000031 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000032 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000033 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000034 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000035 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000036 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000037 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000038 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000039 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003e | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003f | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000040 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000041 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000042 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000043 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000044 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000045 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000046 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000047 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000048 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000049 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004e | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004f | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000050 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000051 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000052 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000053 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000054 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000055 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000056 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000057 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000058 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000059 | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005a | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005b | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005c | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005d | registered_asset |
| unknown | k_atlas | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005e | registered_asset |

## Garantias de nao execucao

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

Registro central de modulos criado em modo somente leitura.
O sistema pode seguir para 081 - K-OS Agent Capability Registry Core.
