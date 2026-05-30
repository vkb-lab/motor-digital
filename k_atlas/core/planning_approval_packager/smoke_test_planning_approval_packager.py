from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.planning_approval_packager.packager import PlanningApprovalPackager
from k_atlas.core.planning_approval_packager.policy import validate_planning_approval_packager_payload


class PlanningApprovalPackagerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_planning_packager_"))
        command_center_dir = self.tmp / "command_center"
        command_center_dir.mkdir(parents=True, exist_ok=True)

        plans = [
            {
                "plan_id": "plan-1",
                "source_intake_task_id": "task-1",
                "mission_id": "mission-1",
                "mission_title": "Missao social",
                "objective": "Criar plano editorial supervisionado do Instagram K-Atlas",
                "layer": "social",
                "risk": "high",
                "status": "planned_waiting_human_review",
                "complexity": {
                    "complexity_score": 4,
                    "complexity_level": "medium",
                    "requires_human_review": True,
                },
                "deliverables": ["pilares editoriais"],
                "acceptance_criteria": ["sem publicacao automatica"],
            },
            {
                "plan_id": "plan-2",
                "source_intake_task_id": "task-2",
                "mission_id": "mission-1",
                "mission_title": "Missao social",
                "objective": "Gerar checklist seguro antes de publicacao",
                "layer": "social",
                "risk": "medium",
                "status": "planned_waiting_human_review",
                "complexity": {
                    "complexity_score": 3,
                    "complexity_level": "medium",
                    "requires_human_review": True,
                },
                "deliverables": ["checklist"],
                "acceptance_criteria": ["sem token em arquivo"],
            },
        ]

        (command_center_dir / "planning_queue.json").write_text(
            json.dumps(plans, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.packager = PlanningApprovalPackager(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
            command_center_dir=command_center_dir,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_publish(self) -> None:
        result = validate_planning_approval_packager_payload({
            "scope": "all",
            "limit": 25,
            "auto_publish": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_publish_blocked", result["reasons"])

    def test_package_plans(self) -> None:
        result = self.packager.package_plans({"scope": "all", "limit": 25})

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "62")
        self.assertEqual(result["summary"]["packages_created"], 2)
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_planning_approval_packager.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_planning_approval_packager.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "62")

    def test_idempotent_packaging_does_not_duplicate(self) -> None:
        first = self.packager.package_plans({"scope": "all", "limit": 25})
        second = self.packager.package_plans({"scope": "all", "limit": 25})

        self.assertEqual(first["summary"]["packages_created"], 2)
        self.assertEqual(second["summary"]["packages_created"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/43_K_Atlas_Planning_Approval_Packager.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
