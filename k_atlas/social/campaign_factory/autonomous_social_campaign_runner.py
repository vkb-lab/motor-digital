# -*- coding: utf-8 -*-
"""K-Social autonomous campaign runner.

Creates supervised campaign operations from business context.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from k_atlas.social.audit.social_approval_queue import SocialApprovalQueue
from k_atlas.social.campaign_factory.social_operation_builder import SocialOperationBuilder
from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter
from k_atlas.social.reports.social_autoreporter import SocialAutoReporter
from k_atlas.social.analytics.social_command_center import SocialCommandCenter


class AutonomousSocialCampaignRunner:
    """Runs a supervised autonomous campaign creation flow."""

    def __init__(
        self,
        social_dir: Optional[Path] = None,
    ) -> None:
        self.social_dir = Path(social_dir) if social_dir else Path(__file__).resolve().parents[1]
        self.reports_dir = self.social_dir / "reports"
        self.memory_dir = self.social_dir / "memory"
        self.requests_dir = self.memory_dir / "autonomous_requests"

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.requests_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_world_football_request(self) -> Dict[str, Any]:
        """Build Parada Atlantida + Chopp Ecobier supervised football-season campaign."""

        return {
            "request_name": "parada_atlantida_chopp_ecobier_temporada_futebol_2026",
            "owner": "K-Atlas Operator",
            "product": "Parada Atlantida + Chopp Ecobier",
            "market": "turismo, gastronomia, experiencia local e encontros para jogos em Florianopolis",
            "personas": [
                "moradores de Florianopolis que querem assistir jogos com amigos",
                "turistas em busca de experiencia local com comida, praia e chopp",
                "grupos que procuram ambiente descontraido para jogos importantes",
                "clientes que valorizam chopp gelado, atendimento e clima de celebracao"
            ],
            "objective": "criar campanha publicitaria supervisionada para a temporada mundial de futebol 2026",
            "channels": [
                "Instagram",
                "Facebook",
                "WhatsApp",
                "Google Business Profile"
            ],
            "duration_days": 10,
            "key_messages": [
                "o encontro do futebol com o clima da praia",
                "Chopp Ecobier gelado para acompanhar os grandes jogos",
                "Parada Atlantida como ponto de encontro para amigos, turistas e torcedores",
                "experiencia local com gastronomia, conversa boa e clima de celebracao",
                "campanha tematica nao oficial, sem uso de marcas ou logos oficiais do torneio"
            ],
            "format_type": "reel",
            "brand_tone": "alegre, local, convidativo, responsavel e comercial",
            "region": "Florianopolis, Santa Catarina, Brasil",
            "language": "pt-BR",
            "seasonal_context": "Copa do Mundo 2026; campanha tematica nao oficial; evitar logos, nomes oficiais e insinuacao de patrocinio"
        }

    def save_request(self, request: Dict[str, Any]) -> Path:
        """Save campaign request for auditability."""

        request_path = self.requests_dir / "parada_atlantida_chopp_ecobier_world_football_2026.json"

        request_payload = {
            "system": "K-Social Autonomous Campaign Request",
            "created_at": self._now(),
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "request": request,
        }

        request_path.write_text(
            json.dumps(request_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return request_path

    def run(self) -> Dict[str, Any]:
        """Run the supervised autonomous campaign flow."""

        request = self.build_world_football_request()
        request_path = self.save_request(request)

        builder = SocialOperationBuilder(
            requests_dir=self.requests_dir,
            reports_dir=self.reports_dir,
        )
        operation_result = builder.run_from_request_data(request)

        approval_queue = SocialApprovalQueue(
            reports_dir=self.reports_dir,
            memory_dir=self.memory_dir,
        ).save_queue()

        snapshot = SocialCockpitAdapter(
            reports_dir=self.reports_dir,
            output_file=self.reports_dir / "social_dashboard_snapshot.json",
        ).save_snapshot()

        daily_report = SocialAutoReporter(
            snapshot_path=self.reports_dir / "social_dashboard_snapshot.json",
            reports_dir=self.reports_dir,
        ).run()

        command_center = SocialCommandCenter(
            social_dir=self.social_dir,
            output_file=self.reports_dir / "social_command_center.json",
        ).save()

        result = {
            "system": "K-Social Autonomous Campaign Runner",
            "created_at": self._now(),
            "campaign": "Parada Atlantida + Chopp Ecobier - Temporada Mundial de Futebol 2026",
            "request_file": str(request_path),
            "operation_file": operation_result["operation_file"],
            "snapshot_total_operations": snapshot["total_operations"],
            "approval_queue_total": approval_queue["total_items"],
            "daily_report_operations": daily_report["summary"]["total_operations"],
            "command_center_operations": command_center["operations"]["total"],
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "brand_safety_notes": [
                "Nao afirmar patrocinio oficial.",
                "Nao usar logos oficiais.",
                "Nao prometer transmissao sem validar direitos.",
                "Manter revisao humana antes de qualquer uso real."
            ],
        }

        result_path = self.reports_dir / "autonomous_campaign_parada_atlantida_chopp_ecobier.json"
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return result


def main() -> None:
    runner = AutonomousSocialCampaignRunner()
    result = runner.run()

    print("K-Social autonomous campaign created.")
    print("Campaign:", result["campaign"])
    print("Request:", result["request_file"])
    print("Operation:", result["operation_file"])
    print("Operations in snapshot:", result["snapshot_total_operations"])
    print("Approval queue:", result["approval_queue_total"])
    print("Command center operations:", result["command_center_operations"])
    print("Publication permission:", result["publication_permission"])
    print("Auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
