# -*- coding: utf-8 -*-
"""Campaign generator for K-Social.

Creates supervised campaign plans and content calendars.
It does not publish posts, does not use real APIs and does not operate browsers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class CampaignGenerator:
    """Generates local campaign plans for human approval."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def generate_campaign(
        self,
        objective: str,
        segments: List[Dict[str, Any]],
        channels: List[str],
        duration_days: int,
        key_messages: List[str],
        campaign_name: str = "K-Social Campaign Draft",
        seasonal_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not objective.strip():
            raise ValueError("objective nao pode ser vazio.")

        if not segments:
            raise ValueError("segments precisa ter ao menos 1 item.")

        if not channels:
            raise ValueError("channels precisa ter ao menos 1 canal.")

        if duration_days <= 0:
            raise ValueError("duration_days precisa ser maior que zero.")

        if not key_messages:
            raise ValueError("key_messages precisa ter ao menos 1 item.")

        clean_channels = []
        for channel in channels:
            channel = channel.strip()
            if channel and channel not in clean_channels:
                clean_channels.append(channel)

        calendar: List[Dict[str, Any]] = []

        for day in range(1, duration_days + 1):
            for channel in clean_channels:
                segment_names = [segment.get("persona", "publico") for segment in segments]
                message = key_messages[(day - 1) % len(key_messages)]

                calendar.append(
                    {
                        "day": day,
                        "channel": channel,
                        "target_segments": segment_names,
                        "content_status": "draft_needs_human_review",
                        "format_suggestion": "post, story, reel ou anuncio supervisionado",
                        "caption_draft": (
                            f"{message}. Conteudo pensado para {', '.join(segment_names)}. "
                            "Revisao humana obrigatoria antes de publicar."
                        ),
                        "cta_suggestion": "falar com atendimento, solicitar proposta ou salvar conteudo",
                        "publish_automatically": False,
                    }
                )

        return {
            "created_at": self._now(),
            "campaign_name": campaign_name,
            "objective": objective,
            "seasonal_context": seasonal_context or "sem sazonalidade definida",
            "channels": clean_channels,
            "duration_days": duration_days,
            "segments_count": len(segments),
            "content_calendar": calendar,
            "allowed_actions": [
                "gerar estrategia",
                "gerar briefing",
                "gerar calendario",
                "gerar auditoria",
            ],
            "blocked_actions": [
                "publicar automaticamente",
                "enviar posts",
                "operar navegador",
                "chamar APIs reais sem modulo aprovado",
            ],
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
        }
