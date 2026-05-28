# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Self Evolution Service

Leitura read-only da camada de autoevolucao supervisionada.
Nao aplica patch.
Nao aprova patch.
Nao altera arquivos.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
SELF_EVOLUTION_DIR = ROOT / "k_atlas" / "self_evolution"


FOLDERS = {
    "patch_requests": SELF_EVOLUTION_DIR / "patch_requests",
    "patch_inbox": SELF_EVOLUTION_DIR / "patch_inbox",
    "patch_approved": SELF_EVOLUTION_DIR / "patch_approved",
    "patch_rejected": SELF_EVOLUTION_DIR / "patch_rejected",
    "snapshots": SELF_EVOLUTION_DIR / "snapshots",
    "rollback": SELF_EVOLUTION_DIR / "rollback",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "error": str(exc),
            "path": str(path),
        }


def load_folder(folder: Path, limit: int = 50) -> List[Dict[str, Any]]:
    folder.mkdir(parents=True, exist_ok=True)

    items: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json"))[-limit:]:
        data = load_json(path)

        item = {
            "name": path.name,
            "path": str(path),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "data": data,
        }

        diff_path = path.with_suffix(".diff")
        if diff_path.exists():
            item["diff_path"] = str(diff_path)
            item["diff"] = diff_path.read_text(encoding="utf-8", errors="replace")
        else:
            item["diff_path"] = None
            item["diff"] = ""

        items.append(item)

    return items


def collect_self_evolution_snapshot(limit: int = 50) -> Dict[str, Any]:
    data = {
        name: load_folder(path, limit=limit)
        for name, path in FOLDERS.items()
    }

    inbox_risks = []
    for item in data.get("patch_inbox", []):
        patch_data = item.get("data", {})
        risk = patch_data.get("risk", {}) if isinstance(patch_data, dict) else {}
        inbox_risks.append(
            {
                "patch": item.get("name"),
                "risk_level": risk.get("risk_level"),
                "risk_score": risk.get("risk_score"),
                "blockers": risk.get("blockers", []),
                "warnings": risk.get("warnings", []),
            }
        )

    return {
        "success": True,
        "created_at": now_iso(),
        "root": str(ROOT),
        "self_evolution_dir": str(SELF_EVOLUTION_DIR),
        "totals": {
            name: len(items)
            for name, items in data.items()
        },
        "risk_summary": inbox_risks,
        "data": data,
        "policy": {
            "mode": "read-only",
            "can_apply_patch": False,
            "can_approve_patch": False,
            "can_reject_patch": False,
            "requires_human_approval": True,
        },
    }
