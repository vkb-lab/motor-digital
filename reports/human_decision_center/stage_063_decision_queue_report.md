# K-Atlas Human Decision Center - Stage 63

Gerado em: 2026-05-30T05:14:32+00:00

## Governanca

- Aprovacao humana obrigatoria: sim
- Publicacao automatica: nao
- Deploy automatico: nao
- API externa real: nao
- Navegador automatico: nao
- Mouse automatico: nao

## Resumo

- Total de pacotes: 4
- Pendentes de decisao: 1
- Ja decididos: 3

## Fila

### 1. Pacote demo para negacao humana

- Package ID: `stage_063_demo_denial`
- Status: `DENIED`
- Risco: `MEDIUM`
- Origem: `reports/planning_approval_packages/stage_063_demo_package_2_denial.json`
- Proxima acao: `NO_AUTOMATIC_ACTION`

Validar bloqueio humano quando o pacote nao possui contexto suficiente.

### 2. Pacote demo para aprovacao humana

- Package ID: `stage_063_demo_approval`
- Status: `APPROVED`
- Risco: `LOW`
- Origem: `reports/planning_approval_packages/stage_063_demo_package_1_approval.json`
- Proxima acao: `NO_AUTOMATIC_ACTION`

Validar se uma campanha interna pode avancar para a proxima etapa supervisionada.

### 3. Pacote demo para pedido de ajustes

- Package ID: `stage_063_demo_adjustments`
- Status: `ADJUSTMENTS_REQUESTED`
- Risco: `MEDIUM`
- Origem: `reports/planning_approval_packages/stage_063_demo_package_3_adjustments.json`
- Proxima acao: `NO_AUTOMATIC_ACTION`

Validar retorno do pacote ao planejamento para revisao antes de qualquer continuidade.

### 4. Planning Approval Packager

- Package ID: `pkg_63f63a8919ff0325`
- Status: `PENDING`
- Risco: `UNKNOWN`
- Origem: `reports/planning_approval_packager/latest_planning_approval_packager.json`
- Proxima acao: `HUMAN_DECISION`

{"approval_packages_total": 25, "candidates_found": 25, "execution_enabled": false, "external_side_effects": "none", "next_action": "revisar pacotes e aprovar manualmente no proximo checkpoint", "packages_created": 25, "planning_queue_total": 75, "real_execution_enabled": false, "scope": "all"}
