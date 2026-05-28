# -*- coding: utf-8 -*-
"""Social auditor for K-Social.

Audits social campaigns before human review.
This module blocks irresponsible automation by design.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class SocialAuditor:
    """Audits campaign plans for basic governance risks."""

    RISKY_TERMS = [
        "garantido",
        "100% garantido",
        "cura",
        "sem risco",
        "resultado imediato",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def audit_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(campaign, dict):
            errors.append("campaign precisa ser um dicionario valido.")
            return self._report(errors, warnings)

        if campaign.get("publication_permission") is not False:
            errors.append("publication_permission precisa ser False no nucleo inicial.")

        if campaign.get("human_review_required") is not True:
            errors.append("human_review_required precisa ser True.")

        if campaign.get("external_api_used") is not False:
            errors.append("external_api_used precisa ser False neste checkpoint.")

        duration_days = campaign.get("duration_days")
        if not isinstance(duration_days, int) or duration_days <= 0:
            errors.append("duration_days precisa ser inteiro positivo.")

        if isinstance(duration_days, int) and duration_days > 90:
            warnings.append("campanha com mais de 90 dias deve ter revisao estrategica extra.")

        channels = campaign.get("channels", [])
        if not channels:
            errors.append("campanha precisa ter ao menos 1 canal.")

        if len(channels) != len(set(channels)):
            warnings.append("canais duplicados foram detectados.")

        content_calendar = campaign.get("content_calendar", [])
        if not content_calendar:
            errors.append("content_calendar nao pode estar vazio.")

        for item in content_calendar:
            if item.get("publish_automatically") is True:
                errors.append("publicacao automatica detectada e bloqueada.")

            caption = str(item.get("caption_draft", "")).lower()
            for risky_term in self.RISKY_TERMS:
                if risky_term in caption:
                    warnings.append(f"termo sensivel detectado: {risky_term}")

        return self._report(errors, warnings)

    def _report(self, errors: List[str], warnings: List[str]) -> Dict[str, Any]:
        return {
            "created_at": self._now(),
            "audit_status": "blocked" if errors else "approved_for_human_review",
            "errors": errors,
            "warnings": warnings,
            "human_review_required": True,
            "publication_permission": False,
            "approved_for_auto_publish": False,
        }
