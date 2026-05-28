# -*- coding: utf-8 -*-
"""
Smoke test do cockpit operacional do K-Atlas OS.

Valida:
- importacao do app
- importacao dos servicos
- disponibilidade do Streamlit
- integracao basica com kernel
- leitura read-only da Self Evolution
- leitura read-only do Cowork Mode

Uso:
python smoke_test_cockpit.py
"""

from __future__ import annotations

import importlib

from cockpit.services.cowork_service import collect_cowork_snapshot
from cockpit.services.kernel_service import cockpit_boot_check, collect_operational_snapshot
from cockpit.services.self_evolution_service import collect_self_evolution_snapshot


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    importlib.import_module("k_atlas_cockpit")

    try:
        import streamlit  # noqa: F401
    except Exception as exc:
        raise SystemExit("Streamlit indisponivel: " + str(exc)) from exc

    boot_check = cockpit_boot_check()

    assert_true(boot_check["success"], "cockpit_boot_check falhou")
    assert_true(boot_check["has_kernel_status"], "kernel_status ausente")
    assert_true(boot_check["agents_total"] >= 1, "nenhum agente encontrado")

    snapshot = collect_operational_snapshot(save_state=False)

    assert_true(snapshot["success"], "snapshot falhou")
    assert_true("agents" in snapshot["data"], "agents ausente")
    assert_true("tasks" in snapshot["data"], "tasks ausente")
    assert_true("memories" in snapshot["data"], "memories ausente")
    assert_true("learning_playbooks" in snapshot["data"], "learning_playbooks ausente")
    assert_true("events" in snapshot["data"], "events ausente")

    self_snapshot = collect_self_evolution_snapshot()

    assert_true(self_snapshot["success"], "self_evolution snapshot falhou")
    assert_true(self_snapshot["policy"]["mode"] == "read-only", "self_evolution nao esta read-only")
    assert_true(self_snapshot["policy"]["can_apply_patch"] is False, "cockpit nao pode aplicar patch")
    assert_true("patch_requests" in self_snapshot["data"], "patch_requests ausente")
    assert_true("patch_inbox" in self_snapshot["data"], "patch_inbox ausente")
    assert_true("rollback" in self_snapshot["data"], "rollback ausente")

    cowork_snapshot = collect_cowork_snapshot()

    assert_true(cowork_snapshot["success"], "cowork snapshot falhou")
    assert_true(cowork_snapshot["policy"]["mode"] == "read-only", "cowork nao esta read-only")
    assert_true(cowork_snapshot["policy"]["can_execute_command"] is False, "cowork nao pode executar comando pelo cockpit")
    assert_true("sessions" in cowork_snapshot["data"], "cowork sessions ausente")
    assert_true("steps" in cowork_snapshot["data"], "cowork steps ausente")
    assert_true("reviews" in cowork_snapshot["data"], "cowork reviews ausente")

    print("Cockpit smoke test OK")
    print("health:", snapshot["health"])
    print("agents_total:", len(snapshot["data"]["agents"]))
    print("self_evolution_totals:", self_snapshot["totals"])
    print("cowork_totals:", cowork_snapshot["totals"])
