from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class PublishingGatewayPanelSmokeTest(unittest.TestCase):
    def test_panel_module_imports(self) -> None:
        module = importlib.import_module("k_atlas.social.publishing_gateway.publishing_gateway_panel")
        self.assertTrue(hasattr(module, "render_social_publishing_gateway_panel"))

    def test_paths_are_defined(self) -> None:
        module = importlib.import_module("k_atlas.social.publishing_gateway.publishing_gateway_panel")
        self.assertEqual(str(module.QUEUE_PATH).replace("\\", "/"), "memory/social_publish_queue.json")
        self.assertEqual(str(module.AUDIT_PATH).replace("\\", "/"), "reports/social_publishing_gateway_audit.jsonl")
        self.assertEqual(str(module.TEST_PAGE_PATH).replace("\\", "/"), "reports/social_test_page_posts.jsonl")


if __name__ == "__main__":
    unittest.main(verbosity=2)