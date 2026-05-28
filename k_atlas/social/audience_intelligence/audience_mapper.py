# -*- coding: utf-8 -*-
"""Audience mapper for K-Social Intelligence System.

This module creates local, supervised audience intelligence records.
It does not call external APIs, does not operate browsers and does not publish content.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AudienceMapper:
    """Creates supervised audience maps and persists them locally."""

    def __init__(self, memory_dir: Optional[Path] = None) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.memory_dir = Path(memory_dir) if memory_dir else base_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / "audience_memory.json"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_memory(self) -> Dict[str, Any]:
        if not self.memory_file.exists():
            return {"audiences": []}

        try:
            with self.memory_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {"audiences": []}

        if "audiences" not in data or not isinstance(data["audiences"], list):
            data = {"audiences": []}

        return data

    def _save_memory(self, data: Dict[str, Any]) -> None:
        with self.memory_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _build_id(self, product: str, market: str, personas: List[str]) -> str:
        raw = f"{product}|{market}|{'|'.join(personas)}|{self._now()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def map_audience(
        self,
        product: str,
        market: str,
        personas: List[str],
        region: str = "Brasil",
        language: str = "pt-BR",
    ) -> Dict[str, Any]:
        if not product.strip():
            raise ValueError("product nao pode ser vazio.")

        if not market.strip():
            raise ValueError("market nao pode ser vazio.")

        if not personas:
            raise ValueError("personas precisa ter ao menos 1 item.")

        clean_personas = [persona.strip() for persona in personas if persona.strip()]
        if not clean_personas:
            raise ValueError("personas precisa ter ao menos 1 item valido.")

        segments: List[Dict[str, Any]] = []

        for index, persona in enumerate(clean_personas, start=1):
            segments.append(
                {
                    "segment_id": f"seg_{index:02d}",
                    "persona": persona,
                    "region": region,
                    "language": language,
                    "interests": [product, market],
                    "likely_needs": [
                        "clareza sobre valor",
                        "prova de confianca",
                        "conteudo simples e direto",
                    ],
                    "content_angles": [
                        "educacao",
                        "beneficio pratico",
                        "prova social supervisionada",
                    ],
                    "risk_notes": [
                        "nao usar dados pessoais sensiveis",
                        "nao prometer resultado garantido",
                        "validar contexto local antes de publicar",
                    ],
                }
            )

        audience_id = self._build_id(product, market, clean_personas)

        record = {
            "audience_id": audience_id,
            "created_at": self._now(),
            "product": product,
            "market": market,
            "region": region,
            "language": language,
            "segments": segments,
            "classification": "social_strategy_draft",
            "source": "manual_input",
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
        }

        memory = self._load_memory()
        memory["audiences"].append(record)
        self._save_memory(memory)

        return record

    def list_audiences(self) -> List[Dict[str, Any]]:
        return self._load_memory().get("audiences", [])
