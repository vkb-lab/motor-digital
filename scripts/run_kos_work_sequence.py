from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "memory" / "kos_governance" / "KOS_SEQUENTIAL_WORK_ORDER_RUNNER_POLICY.json"
REPORT_DIR = ROOT / "reports"


@dataclass(frozen=True)
class WorkStep:
    id: str
    objective: str
    allowed_files: tuple[str, ...]
    forbidden_files: tuple[str, ...]
    create: Callable[[], None]
    validations: tuple[str, ...]
    tests: tuple[str, ...]
    report_prefix: str


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_step_report(prefix: str, title: str, lines: list[str]) -> None:
    body = ["# " + title, "", *lines, ""]
    write_text(f"reports/{prefix}_{stamp()}.md", "\n".join(body))


def create_personal_data_estate_guardian() -> None:
    write_step_report(
        "KOS_PERSONAL_DATA_ESTATE_GUARDIAN_PLAN",
        "KOS Personal Data Estate Guardian Plan",
        [
            "Scope: registry, skill, status script and tests only.",
            "No external API access.",
            "No secret exposure.",
            "Personal data is treated as private estate.",
        ],
    )


def create_local_storage_estate_auditor() -> None:
    write_step_report(
        "KOS_LOCAL_STORAGE_ESTATE_PLAN",
        "KOS Local Storage Estate Plan",
        [
            "Scope: declared repository roots only.",
            "No full disk scan.",
            "No mass hashing.",
            "No file relocation.",
        ],
    )


def create_render_deploy_control_plane() -> None:
    write_step_report(
        "KOS_RENDER_DEPLOY_CONTROL_PLANE",
        "KOS Render Deploy Control Plane",
        [
            "Scope: deploy readiness only.",
            "No deploy execution.",
            "No render.yaml change.",
            "No secrets.",
        ],
    )


def create_custom_navigation_registry() -> None:
    write_step_report(
        "KOS_CUSTOM_NAVIGATION_PLAN",
        "KOS Custom Navigation Plan",
        [
            "Scope: registry and status only.",
            "No page relocation.",
            "No page removal.",
            "No app.py change in this step.",
        ],
    )


def create_operator_intent_router_isolated() -> None:
    write_step_report(
        "KOS_OPERATOR_INTENT_ROUTER_PLAN",
        "KOS Operator Intent Router Plan",
        [
            "Scope: isolated router script and tests only.",
            "No change to pages/KOS_Operator_Chat.py.",
            "No external actions.",
        ],
    )


STEPS = (
    WorkStep(
        id="personal_data_estate_guardian",
        objective="Create private personal data estate guardrails.",
        allowed_files=(
            "memory/kos_governance/KOS_PERSONAL_DATA_ESTATE_REGISTRY.json",
            "memory/kos_skills/KOS_SKILL_PERSONAL_DATA_ESTATE_GUARDIAN_V1.md",
            "scripts/run_personal_data_estate_status.py",
            "tests/test_kos_personal_data_estate_guardian.py",
            "reports/KOS_PERSONAL_DATA_ESTATE_GUARDIAN_PLAN_<timestamp>.md",
        ),
        forbidden_files=("app.py", "pages/", "render.yaml", "local_runtime/"),
        create=create_personal_data_estate_guardian,
        validations=("registry_exists", "skill_exists", "status_script_json"),
        tests=("tests/test_kos_personal_data_estate_guardian.py",),
        report_prefix="KOS_PERSONAL_DATA_ESTATE_GUARDIAN_PLAN",
    ),
    WorkStep(
        id="local_storage_estate_auditor",
        objective="Create repo-scoped local storage estate status without broad scanning.",
        allowed_files=(
            "memory/kos_governance/KOS_LOCAL_STORAGE_ESTATE_REGISTRY.json",
            "scripts/run_local_storage_estate_status.py",
            "tests/test_kos_local_storage_estate.py",
            "reports/KOS_LOCAL_STORAGE_ESTATE_PLAN_<timestamp>.md",
        ),
        forbidden_files=("app.py", "pages/", "render.yaml", "local_runtime/", "drive_root"),
        create=create_local_storage_estate_auditor,
        validations=("registry_exists", "repo_roots_only", "status_script_json"),
        tests=("tests/test_kos_local_storage_estate.py",),
        report_prefix="KOS_LOCAL_STORAGE_ESTATE_PLAN",
    ),
    WorkStep(
        id="render_deploy_control_plane",
        objective="Create Render read-only deploy readiness control plane.",
        allowed_files=(
            "memory/kos_governance/KOS_RENDER_CLOUD_RUNTIME_POLICY.json",
            "scripts/run_render_deploy_readiness_status.py",
            "tests/test_kos_render_deploy_readiness.py",
            "reports/KOS_RENDER_DEPLOY_CONTROL_PLANE_<timestamp>.md",
        ),
        forbidden_files=("app.py", "pages/", "render.yaml", "local_runtime/", "secrets"),
        create=create_render_deploy_control_plane,
        validations=("policy_exists", "app_render_exists", "status_script_json"),
        tests=("tests/test_kos_render_deploy_readiness.py",),
        report_prefix="KOS_RENDER_DEPLOY_CONTROL_PLANE",
    ),
    WorkStep(
        id="custom_navigation_registry",
        objective="Create custom navigation registry before changing UI.",
        allowed_files=(
            "memory/kos_governance/KOS_CUSTOM_NAVIGATION_REGISTRY.json",
            "scripts/run_kos_navigation_status.py",
            "tests/test_kos_custom_navigation.py",
            "reports/KOS_CUSTOM_NAVIGATION_PLAN_<timestamp>.md",
        ),
        forbidden_files=("app.py", "pages/", "render.yaml", "local_runtime/"),
        create=create_custom_navigation_registry,
        validations=("registry_exists", "core_paths_declared", "status_script_json"),
        tests=("tests/test_kos_custom_navigation.py",),
        report_prefix="KOS_CUSTOM_NAVIGATION_PLAN",
    ),
    WorkStep(
        id="operator_intent_router_isolated",
        objective="Create isolated operator intent router without wiring it to Operator Chat yet.",
        allowed_files=(
            "scripts/kos_operator_intent_router.py",
            "tests/test_kos_operator_intent_router.py",
            "reports/KOS_OPERATOR_INTENT_ROUTER_PLAN_<timestamp>.md",
        ),
        forbidden_files=("app.py", "pages/KOS_Operator_Chat.py", "render.yaml", "local_runtime/"),
        create=create_operator_intent_router_isolated,
        validations=("script_exists", "routes_known_intents", "no_external_actions"),
        tests=("tests/test_kos_operator_intent_router.py",),
        report_prefix="KOS_OPERATOR_INTENT_ROUTER_PLAN",
    ),
)

SEQUENCES = {
    "personal_data_foundation": STEPS,
}


def policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def step_to_dict(step: WorkStep) -> dict:
    return {
        "id": step.id,
        "objective": step.objective,
        "allowed_files": list(step.allowed_files),
        "forbidden_files": list(step.forbidden_files),
        "validations": list(step.validations),
        "tests": list(step.tests),
        "report_prefix": step.report_prefix,
    }


def list_sequences() -> dict:
    return {
        "status": "KOS_WORK_SEQUENCE_LIST_READY",
        "policy_status": policy().get("status"),
        "sequences": [
            {"id": key, "steps": [step.id for step in value]}
            for key, value in SEQUENCES.items()
        ],
    }


def plan_sequence(sequence: str) -> dict:
    steps = SEQUENCES.get(sequence)
    if not steps:
        return {"status": "KOS_WORK_SEQUENCE_UNKNOWN", "sequence": sequence}
    return {
        "status": "KOS_WORK_SEQUENCE_PLAN_READY",
        "sequence": sequence,
        "mode": "plan",
        "rules": policy().get("rules", []),
        "steps": [step_to_dict(step) for step in steps],
    }


def run_tests(test_paths: tuple[str, ...]) -> dict:
    cmd = [sys.executable, "-m", "pytest", *test_paths, "-q"]
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def run_sequence(sequence: str) -> dict:
    steps = SEQUENCES.get(sequence)
    if not steps:
        return {"status": "KOS_WORK_SEQUENCE_UNKNOWN", "sequence": sequence}

    results = []
    for step in steps:
        result = {"id": step.id, "phase": "running"}
        try:
            step.create()
            test_result = run_tests(step.tests)
            result["test_result"] = test_result
            result["phase"] = "passed" if test_result["ok"] else "failed"
        except Exception as exc:
            result["phase"] = "failed"
            result["error"] = f"{exc.__class__.__name__}: {exc}"
        results.append(result)
        if result["phase"] != "passed":
            write_text(
                f"reports/KOS_WORK_SEQUENCE_FAILURE_{stamp()}.md",
                "# KOS Work Sequence Failure\n\n"
                f"Sequence: {sequence}\n\n"
                f"Failed step: {step.id}\n\n"
                f"Result:\n\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n",
            )
            return {"status": "KOS_WORK_SEQUENCE_FAILED", "sequence": sequence, "results": results}

    return {"status": "KOS_WORK_SEQUENCE_PASSED", "sequence": sequence, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="K-OS Sequential Work Order Runner")
    parser.add_argument("--mode", choices=["list", "plan", "run"], required=True)
    parser.add_argument("--sequence", default="")
    args = parser.parse_args()

    if args.mode == "list":
        payload = list_sequences()
    elif args.mode == "plan":
        payload = plan_sequence(args.sequence)
    else:
        payload = run_sequence(args.sequence)

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
