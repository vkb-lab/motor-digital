from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.saas_factory.builder_agent.builder import SaaSBuilderAgent
from k_atlas.saas_factory.builder_agent.spec import build_product_spec

from .workflow_spec import build_default_saas_workflow_payload, validate_saas_workflow_payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SaaSFactoryWorkflowRunner:
    def __init__(
        self,
        products_root: str | Path = "k_atlas/saas_factory/products",
        reports_root: str | Path = "reports/saas_factory/workflows",
    ) -> None:
        self.products_root = Path(products_root)
        self.reports_root = Path(reports_root)

    def run(self, payload: Mapping[str, Any] | None = None, requested_by: str = "human_operator") -> dict[str, Any]:
        workflow_id = str(uuid4())
        data = dict(payload or build_default_saas_workflow_payload())
        validation = validate_saas_workflow_payload(data)

        started_at = utc_now_iso()
        steps: list[dict[str, Any]] = []

        if not validation["ok"]:
            report = {
                "ok": False,
                "workflow_id": workflow_id,
                "status": "blocked_by_policy",
                "started_at": started_at,
                "finished_at": utc_now_iso(),
                "requested_by": requested_by,
                "validation": validation,
                "payload": data,
                "steps": steps,
            }
            self._save_report(workflow_id, report)
            return report

        spec = build_product_spec(data)
        steps.append({
            "step": "spec_created",
            "ok": True,
            "spec": spec.to_dict(),
        })

        builder = SaaSBuilderAgent(output_root=self.products_root)
        build_result = builder.generate_app_module(data)

        steps.append({
            "step": "mvp_generated",
            "ok": bool(build_result.get("ok")),
            "result": build_result,
        })

        product_dir = Path(build_result["product_dir"])
        compile_checks = self._compile_product(product_dir)

        steps.append({
            "step": "compile_validation",
            "ok": compile_checks["ok"],
            "result": compile_checks,
        })

        deploy_plan = self._build_deploy_plan(product_dir, spec.slug)

        steps.append({
            "step": "deploy_plan_prepared",
            "ok": True,
            "result": deploy_plan,
        })

        ok = all(bool(step.get("ok")) for step in steps)

        report = {
            "ok": ok,
            "workflow_id": workflow_id,
            "checkpoint": "38",
            "name": "SaaS Factory Workflow Real",
            "status": "completed" if ok else "failed",
            "started_at": started_at,
            "finished_at": utc_now_iso(),
            "requested_by": requested_by,
            "validation": validation,
            "payload": data,
            "product_dir": str(product_dir).replace("\\", "/"),
            "steps": steps,
            "next_actions": [
                "revisar produto gerado",
                "rodar localmente o app do MVP",
                "aprovar deploy supervisionado",
                "registrar como produto reutilizavel no K-Atlas",
            ],
        }

        self._save_report(workflow_id, report)
        return report

    def _compile_product(self, product_dir: Path) -> dict[str, Any]:
        files = [
            product_dir / "app.py",
            product_dir / "modules" / "core.py",
            product_dir / "tests" / "smoke_test.py",
        ]

        compiled: list[str] = []
        errors: list[str] = []

        for file in files:
            try:
                py_compile.compile(str(file), doraise=True)
                compiled.append(str(file).replace("\\", "/"))
            except Exception as exc:
                errors.append(f"{file}: {type(exc).__name__}: {exc}")

        return {
            "ok": len(errors) == 0,
            "compiled": compiled,
            "errors": errors,
        }

    def _build_deploy_plan(self, product_dir: Path, slug: str) -> dict[str, Any]:
        deploy_plan = {
            "status": "prepared_not_deployed",
            "product_slug": slug,
            "product_dir": str(product_dir).replace("\\", "/"),
            "local_run_command": f"cd {product_dir} && streamlit run app.py",
            "render_ready": False,
            "requires_human_review": True,
            "notes": [
                "deploy automatico bloqueado neste checkpoint",
                "produto pronto para revisao local",
                "deploy real sera tratado no Checkpoint 39",
            ],
        }

        (product_dir / "deploy_plan.json").write_text(
            json.dumps(deploy_plan, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return deploy_plan

    def _save_report(self, workflow_id: str, report: dict[str, Any]) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)

        latest_path = self.reports_root / "latest_saas_factory_workflow.json"
        run_path = self.reports_root / f"{workflow_id}.json"

        latest_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        run_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
