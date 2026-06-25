from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "memory" / "kos_governance" / "KOS_ORIGIN_CORE_REGISTRY.json"


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_origin_core_registry_exists_and_status_is_active():
    data = load_registry()
    assert data["status"] == "KOS_ORIGIN_CORE_REGISTRY_ACTIVE"
    assert data["first_commit"] == "eb0db4e"
    assert data["first_commit_title"] == "Criar app.py com interface Streamlit - Torre de Controle IA"


def test_origin_core_cycle_contains_required_steps():
    data = load_registry()
    cycle = data["core_cycle"]
    for step in [
        "human_intent",
        "memory_context",
        "routing",
        "risk_assessment",
        "safe_execution_or_human_gate",
        "evidence",
        "reusable_learning",
    ]:
        assert step in cycle


def test_origin_core_home_and_cloud_readonly_contract():
    data = load_registry()
    assert data["official_home"] == "app.py"
    assert data["cloud_readonly"] == "app_render.py"
    assert "pages/KOS_Operator_Chat.py" in data["priority_core_files"]
    assert "scripts/run_gmail_operator.py" in data["priority_core_files"]
    assert data["external_tools_role"] == "subordinate_tools_not_replacements"


def test_origin_core_skill_and_doctrine_exist():
    skill = ROOT / "memory" / "kos_skills" / "KOS_SKILL_ORIGIN_TO_DESTINATION_REASONING_V1.md"
    doctrine = ROOT / "memory" / "kos_governance" / "KOS_UNICORN_BUILDER_OS_DOCTRINE_V1.md"
    assert skill.exists()
    assert doctrine.exists()
    assert "Unicorn Builder OS" in doctrine.read_text(encoding="utf-8")
    assert "human_intent" in skill.read_text(encoding="utf-8")


def test_origin_core_status_script_compiles_and_returns_json():
    script = ROOT / "scripts" / "run_kos_origin_core_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run(
        [sys.executable, str(script), "--mode", "status"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_ORIGIN_CORE_STATUS_READY"
    assert data["registry_status"] == "KOS_ORIGIN_CORE_REGISTRY_ACTIVE"
    assert data["official_home_exists"] is True
    assert data["cloud_readonly_exists"] is True
    assert data["next_patch_recommended"] == "K-OS Custom Navigation v1"


def test_origin_core_files_do_not_contain_secret_material():
    files = [
        REGISTRY_PATH,
        ROOT / "memory" / "kos_governance" / "KOS_UNICORN_BUILDER_OS_DOCTRINE_V1.md",
        ROOT / "memory" / "kos_skills" / "KOS_SKILL_ORIGIN_TO_DESTINATION_REASONING_V1.md",
        ROOT / "scripts" / "run_kos_origin_core_status.py",
    ]
    forbidden = [
        "token_gmail",
        "client_secret",
        "refresh_token",
        "access_token",
        "GMAIL_TOKEN_JSON",
        "GEMINI_API_KEY=",
        "META_ACCESS_TOKEN=",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    for marker in forbidden:
        assert marker not in joined
