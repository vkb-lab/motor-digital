from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_deploy_payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(args: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        return {
            "ok": completed.returncode == 0,
            "command": " ".join(args),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": " ".join(args),
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


class DeployPipelineAssistant:
    def __init__(self, reports_root: str | Path = "reports/deploy_pipeline") -> None:
        self.reports_root = Path(reports_root)

    def run_assisted_check(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or {
            "target": "render",
            "service": "k-atlas-os",
            "auto_deploy": False,
            "force_push": False,
            "production_mutation": False,
            "official_publish": False,
        })

        validation = validate_deploy_payload(data)

        checks = {
            "app_py_exists": Path("app.py").exists(),
            "requirements_exists": Path("requirements.txt").exists(),
            "runtime_txt_exists": Path("runtime.txt").exists(),
            "render_yaml_exists": Path("render.yaml").exists(),
            "git_repo": Path(".git").exists(),
            "k_atlas_package": Path("k_atlas").exists(),
            "streamlit_pages": len(list(Path("pages").glob("*.py"))) if Path("pages").exists() else 0,
        }

        git_status = run_command(["git", "status", "--short"])
        git_branch = run_command(["git", "branch", "--show-current"])
        git_log = run_command(["git", "log", "--oneline", "-5"])

        warnings: list[str] = []

        if not checks["app_py_exists"]:
            warnings.append("app.py_missing")

        if not checks["requirements_exists"]:
            warnings.append("requirements.txt_missing")

        if git_status["stdout"].strip():
            warnings.append("git_has_uncommitted_changes")

        if not validation["ok"]:
            warnings.append("deploy_payload_blocked")

        deploy_plan = {
            "mode": "assisted",
            "target": data.get("target", "render"),
            "service": data.get("service", "k-atlas-os"),
            "auto_deploy": False,
            "manual_steps": [
                "revisar git status",
                "rodar smoke tests principais",
                "fazer commit dos arquivos aprovados",
                "fazer git push origin main",
                "acompanhar Render Events",
                "abrir URL publica e rodar health check manual",
            ],
            "rollback_plan": [
                "identificar ultimo commit estavel",
                "usar Render Manual Deploy para commit anterior ou git revert",
                "validar app publico apos rollback",
                "registrar evento no AutoReporter",
            ],
        }

        report = {
            "ok": validation["ok"] and checks["app_py_exists"] and checks["requirements_exists"],
            "checkpoint": "39",
            "name": "Deploy Pipeline Assistido",
            "run_id": run_id,
            "generated_at": utc_now_iso(),
            "status": "ready_for_human_review" if validation["ok"] else "blocked",
            "payload": data,
            "validation": validation,
            "checks": checks,
            "warnings": warnings,
            "git": {
                "branch": git_branch,
                "status": git_status,
                "last_commits": git_log,
            },
            "deploy_plan": deploy_plan,
            "side_effects": "report_only_no_deploy",
        }

        self._save_report(run_id, report)
        return report

    def _save_report(self, run_id: str, report: dict[str, Any]) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)

        latest = self.reports_root / "latest_deploy_pipeline_report.json"
        run_file = self.reports_root / f"{run_id}.json"

        latest.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_file.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
