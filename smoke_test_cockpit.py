# -*- coding: utf-8 -*-
"""
Smoke test do cockpit operacional do K-Atlas OS.

Valida:
- importacao do app
- importacao dos servicos
- disponibilidade do Streamlit
- integracao basica com kernel
- snapshot operacional minimo

Uso:
python smoke_test_cockpit.py
"""

from __future__ import annotations

import importlib

from cockpit.services.kernel_service import cockpit_boot_check, collect_operational_snapshot


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

    print("Cockpit smoke test OK")
    print("health:", snapshot["health"])
    print("agents_total:", len(snapshot["data"]["agents"]))
