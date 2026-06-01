# K-OS Recovery Plan

- Recovery Plan ID: rpb_be687cf9460f
- Status: plan_blocked_review_required
- Scope: controlled_recovery_scope
- Readiness level: review_required
- Risk level: medium
- Plan hash: 57c5ff16f97ab3450279ded3966e63997e646f95581a592c719412eb60355d71
- Executes recovery: False
- Executes rollback: False
- Deletes data: False
- Modifies target files: False
- Runs git reset: False
- Runs git force push: False

## Plan steps

- 1 | preservar_evidencias | executes_recovery=False | destructive=False
- 2 | confirmar_escopo | executes_recovery=False | destructive=False
- 3 | validar_readiness | executes_recovery=False | destructive=False
- 4 | gate_aprovacao | executes_recovery=False | destructive=False
- 5 | execucao_futura_manual | executes_recovery=False | destructive=False

## Blockers

- readiness_not_controlled_ready
- {'checkpoint': '053', 'blocker': 'blocked_status_present'}
- {'checkpoint': '054', 'blocker': 'blocked_status_present'}
- {'checkpoint': '056', 'blocker': 'blocked_status_present'}