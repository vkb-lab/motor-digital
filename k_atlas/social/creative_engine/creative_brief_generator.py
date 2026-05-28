# -*- coding: utf-8 -*-
"""Creative brief generator for K-Social.

Generates supervised briefs for social content, image AI, video AI, reels and ads.
It never publishes content and never calls external APIs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class CreativeBriefGenerator:
    """Creates structured creative briefs for supervised production."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def generate_brief(
        self,
        product: str,
        objective: str,
        target_audience: List[str],
        key_messages: List[str],
        format_type: str = "reel",
        brand_tone: str = "profissional, claro e direto",
        seasonal_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not product.strip():
            raise ValueError("product nao pode ser vazio.")

        if not objective.strip():
            raise ValueError("objective nao pode ser vazio.")

        if not target_audience:
            raise ValueError("target_audience precisa ter ao menos 1 item.")

        if not key_messages:
            raise ValueError("key_messages precisa ter ao menos 1 item.")

        return {
            "created_at": self._now(),
            "product": product,
            "objective": objective,
            "target_audience": target_audience,
            "key_messages": key_messages,
            "format_type": format_type,
            "brand_tone": brand_tone,
            "seasonal_context": seasonal_context or "sem sazonalidade definida",
            "creative_direction": {
                "hook": "abrir com uma dor ou desejo claro do publico",
                "body": "explicar o valor de forma simples e local",
                "cta": "convidar para proximo passo sem pressao enganosa",
            },
            "ai_image_ready": {
                "enabled_for_future": True,
                "prompt_requirements": [
                    "descrever cena",
                    "descrever estilo visual",
                    "evitar marcas de terceiros sem autorizacao",
                    "validar direitos de uso antes de publicar",
                ],
            },
            "ai_video_ready": {
                "enabled_for_future": True,
                "script_requirements": [
                    "roteiro curto",
                    "cenas numeradas",
                    "legendas planejadas",
                    "revisao humana obrigatoria",
                ],
            },
            "reels_ready": {
                "enabled_for_future": True,
                "duration_hint": "15 a 45 segundos",
                "structure": ["gancho", "valor", "prova", "chamada para acao"],
            },
            "ads_ready": {
                "enabled_for_future": True,
                "requires_budget_approval": True,
                "requires_legal_review": True,
            },
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
        }
