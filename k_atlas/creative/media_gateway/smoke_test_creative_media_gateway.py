from __future__ import annotations

import json
import py_compile
import tempfile
import unittest
from pathlib import Path

from k_atlas.creative.media_gateway.brief import build_custom_brief, build_default_k_atlas_brief
from k_atlas.creative.media_gateway.export_package import export_default_k_atlas_creative_package
from k_atlas.creative.media_gateway.governance import validate_creative_media_payload
from k_atlas.creative.media_gateway.package_builder import build_creative_media_package
from k_atlas.creative.media_gateway.prompt_pack import build_prompt_pack


class CreativeMediaGatewaySmokeTest(unittest.TestCase):
    def test_default_brief(self) -> None:
        brief = build_default_k_atlas_brief()
        self.assertEqual(brief.project_name, "K-Atlas OS")
        self.assertIn("supervisão humana", brief.objective)

    def test_prompt_pack(self) -> None:
        brief = build_default_k_atlas_brief()
        pack = build_prompt_pack(brief)

        self.assertFalse(pack["external_api_used"])
        self.assertFalse(pack["generation_allowed"])
        self.assertIn("hero_image", pack["prompts"])

    def test_governance_blocks_external_api_without_vault(self) -> None:
        result = validate_creative_media_payload({
            "external_api_enabled": True,
            "official_publish": False,
        })

        self.assertFalse(result["ok"])
        self.assertIn("external_api_requires_credential_vault", result["reasons"])

    def test_build_custom_package(self) -> None:
        brief = build_custom_brief(
            project_name="Teste",
            objective="Criar pacote",
            target_audience="Founders",
            offer="Sistema IA",
        )
        package = build_creative_media_package(brief)

        self.assertTrue(package["ok"])
        self.assertEqual(package["status"], "ready_for_human_review")
        self.assertFalse(package["official_publish_allowed"])

    def test_export_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "package.json"
            report = export_default_k_atlas_creative_package(str(output))

            self.assertTrue(output.exists())
            self.assertEqual(report["checkpoint"], "32")

            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(loaded["name"], "Creative Media Gateway")

    def test_page_compiles(self) -> None:
        self.assertTrue(Path("pages/13_K_Atlas_Creative_Media_Gateway.py").exists())
        py_compile.compile("pages/13_K_Atlas_Creative_Media_Gateway.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)