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
- leitura read-only do Prompt Generator
- leitura read-only da Lousa Operacional

Uso:
python smoke_test_cockpit.py
"""

from __future__ import annotations

import importlib

from cockpit.services.cowork_service import collect_cowork_snapshot
from cockpit.services.kernel_service import cockpit_boot_check, collect_operational_snapshot
from cockpit.services.lousa_service import collect_lousa_snapshot
from cockpit.services.prompt_generator_service import collect_prompt_generator_snapshot
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

    cowork_snapshot = collect_cowork_snapshot()

    assert_true(cowork_snapshot["success"], "cowork snapshot falhou")
    assert_true(cowork_snapshot["policy"]["mode"] == "read-only", "cowork nao esta read-only")
    assert_true(cowork_snapshot["policy"]["can_execute_command"] is False, "cowork nao pode executar comando pelo cockpit")

    prompt_snapshot = collect_prompt_generator_snapshot()

    assert_true(prompt_snapshot["success"], "prompt generator snapshot falhou")
    assert_true(prompt_snapshot["policy"]["mode"] == "read-only", "prompt generator nao esta read-only")
    assert_true(prompt_snapshot["policy"]["can_execute_commands"] is False, "prompt generator nao pode executar comandos")

    lousa_snapshot = collect_lousa_snapshot()

    assert_true(lousa_snapshot["success"], "lousa snapshot falhou")
    assert_true(lousa_snapshot["policy"]["mode"] == "read-only", "lousa nao esta read-only")
    assert_true(lousa_snapshot["policy"]["can_execute_commands"] is False, "lousa nao pode executar comandos")
    assert_true("boards" in lousa_snapshot["data"], "lousa boards ausente")
    assert_true("cards" in lousa_snapshot["data"], "lousa cards ausente")
    assert_true("professor_review" in lousa_snapshot["lanes"], "lane professor_review ausente")

    print("Cockpit smoke test OK")
    print("health:", snapshot["health"])
    print("agents_total:", len(snapshot["data"]["agents"]))
    print("self_evolution_totals:", self_snapshot["totals"])
    print("cowork_totals:", cowork_snapshot["totals"])
    print("prompt_generator_totals:", prompt_snapshot["totals"])
    print("lousa_totals:", lousa_snapshot["totals"])
