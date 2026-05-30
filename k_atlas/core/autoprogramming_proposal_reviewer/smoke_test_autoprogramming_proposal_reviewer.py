from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autoprogramming_proposal_reviewer.policy import validate_review_payload
from k_atlas.core.autoprogramming_proposal_reviewer.reviewer import AutoprogrammingProposalReviewer


class AutoprogrammingProposalReviewerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autoprog_reviewer_"))
        self.proposals_path = self.tmp / "memory" / "assisted_autoprogramming" / "proposal_queue.json"
        self.proposals_path.parent.mkdir(parents=True, exist_ok=True)

        proposals = [
            {
                "proposal_id": "proposal-1",
                "checkpoint": "66",
                "action": "create_module",
                "objective": "Criar modulo seguro.",
                "status": "waiting_human_review",
                "file_plans": [
                    {
                        "action": "create_module",
                        "path": "k_atlas/core/demo/README.md",
                        "content": "demo",
                    }
                ],
                "file_validations": [
                    {
                        "ok": True,
                        "status": "file_plan_allowed",
                    }
                ],
                "execution_enabled": False,
                "real_execution_enabled": False,
            }
        ]

        self.proposals_path.write_text(
            json.dumps(proposals, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.reviewer = AutoprogrammingProposalReviewer(
            proposals_path=self.proposals_path,
            review_dir=self.tmp / "memory" / "reviewer",
            reports_dir=self.tmp / "reports",
            live_dir=self.tmp / "live",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_deploy(self) -> None:
        result = validate_review_payload({
            "decision": "approve_for_apply_package",
            "notes": "ok",
            "auto_deploy": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_deploy_blocked", result["reasons"])

    def test_build_review_queue(self) -> None:
        result = self.reviewer.build_review_queue()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "66")
        self.assertEqual(result["summary"]["reviews_created"], 1)
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "proposal_review_queue.json").exists())
        self.assertTrue((self.tmp / "reports" / "latest_autoprogramming_proposal_reviewer.json").exists())

    def test_decide_review(self) -> None:
        result = self.reviewer.build_review_queue()
        review_id = result["created_reviews"][0]["review_id"]

        decision = self.reviewer.decide(
            review_id=review_id,
            decision="approve_for_apply_package",
            reviewer="tester",
            notes="aprovado em teste supervisionado",
        )

        self.assertTrue(decision["ok"])
        self.assertEqual(decision["status"], "decision_registered")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/66_K_Atlas_Autoprogramming_Proposal_Reviewer.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
