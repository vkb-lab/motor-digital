# -*- coding: utf-8 -*-
"""
Smoke test de governanca da camada Self Evolution.

Valida:
- patches aprovados existem
- patches aprovados continuam sem auto_apply
- approval nao libera aplicacao automatica
- risco exige approval humano
- proposta possui diff e conteudo proposto

Uso:
python smoke_test_self_evolution_governance.py
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APPROVED_DIR = ROOT / "k_atlas" / "self_evolution" / "patch_approved"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)

    approved_files = sorted(APPROVED_DIR.glob("*.json"))

    assert_true(len(approved_files) >= 1, "Nenhum patch aprovado encontrado para validar governanca.")

    checked = 0

    for path in approved_files:
        data = json.loads(path.read_text(encoding="utf-8"))

        approval = data.get("approval", {})
        governance = data.get("governance", {})
        risk = data.get("risk", {})

        assert_true(approval.get("status") == "approved", "Patch aprovado sem approval.status correto: " + str(path))
        assert_true(approval.get("can_apply") is False, "Approval nao pode liberar aplicacao automatica: " + str(path))
        assert_true(governance.get("can_auto_apply") is False, "Governance can_auto_apply deve ser false: " + str(path))
        assert_true(governance.get("requires_human_approval") is True, "Approval humano deve ser obrigatorio: " + str(path))
        assert_true(risk.get("requires_human_approval") is True, "Risk deve exigir approval humano: " + str(path))
        assert_true(bool(data.get("diff")), "Patch aprovado precisa manter diff auditavel: " + str(path))
        assert_true(bool(data.get("proposed_content")), "Patch aprovado precisa manter proposed_content: " + str(path))

        checked += 1

    print("Self Evolution governance smoke test OK")
    print("approved_patches_checked:", checked)
