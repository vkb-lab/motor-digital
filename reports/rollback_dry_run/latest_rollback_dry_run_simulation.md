# K-OS Rollback Dry Run Simulation

- Simulation ID: rds_f88727f867b9
- Status: simulated_blocked
- OK: True
- Release ID: rbg_ff638f05f0bd
- Release status: blocked
- Rollback Plan ID: rbp_8004b3ca46e3
- Dry-run hash: a0acc0f60e22ce27811ece12e97fb581b8455b42a0bade9fa36f531dadaa4a0a
- Safely blocked by release gate: True
- Executes rollback: False
- Deletes data: False
- Modifies files: False
- Runs git reset: False
- Runs git force push: False

## Simulation steps

- 1 | validar_gate_de_release | result=release_gate_checked | executes_rollback=False
- 2 | validar_plano_rollback | result=rollback_plan_checked | executes_rollback=False
- 3 | simular_ponto_restauracao | result=restore_point_simulated | executes_rollback=False
- 4 | simular_validacao_pos_rollback | result=post_rollback_validation_simulated | executes_rollback=False

## Blockers

- Nenhum blocker.