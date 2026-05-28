# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[2]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def load_patch(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require_human_approval(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": False,
        "approved": False,
        "message": "Approval humano obrigatorio. Patch nao pode ser aplicado automaticamente.",
        "patch_id": data.get("patch_id"),
        "can_auto_apply": False,
        "requires_human_approval": True,
    }


def approve_patch(patch_path: str | Path, approved_by: str, reason: str, root_path: Optional[str | Path] = None) -> Dict[str, Any]:
    if not approved_by.strip():
        raise ValueError("Campo obrigatorio ausente: approved_by")
    if not reason.strip():
        raise ValueError("Campo obrigatorio ausente: reason")

    base_root = Path(root_path) if root_path else ROOT
    approved_dir = base_root / "k_atlas" / "self_evolution" / "patch_approved"

    source_path = Path(patch_path)
    data = load_patch(source_path)
    data["approval"] = {
        "status": "approved",
        "approved_by": approved_by.strip(),
        "reason": reason.strip(),
        "approved_at": now_iso(),
        "can_apply": False,
        "note": "Aprovado para revisao futura. Aplicacao automatica ainda bloqueada.",
    }
    data["status"] = "approved_waiting_manual_application"

    destination = approved_dir / source_path.name
    write_json_atomic(destination, data)

    diff_source = source_path.with_suffix(".diff")
    if diff_source.exists():
        shutil.copy2(diff_source, destination.with_suffix(".diff"))

    return {"success": True, "approved": True, "approved_path": str(destination), "can_auto_apply": False}


def reject_patch(patch_path: str | Path, rejected_by: str, reason: str, root_path: Optional[str | Path] = None) -> Dict[str, Any]:
    if not rejected_by.strip():
        raise ValueError("Campo obrigatorio ausente: rejected_by")
    if not reason.strip():
        raise ValueError("Campo obrigatorio ausente: reason")

    base_root = Path(root_path) if root_path else ROOT
    rejected_dir = base_root / "k_atlas" / "self_evolution" / "patch_rejected"

    source_path = Path(patch_path)
    data = load_patch(source_path)
    data["approval"] = {
        "status": "rejected",
        "rejected_by": rejected_by.strip(),
        "reason": reason.strip(),
        "rejected_at": now_iso(),
    }
    data["status"] = "rejected"

    destination = rejected_dir / source_path.name
    write_json_atomic(destination, data)

    diff_source = source_path.with_suffix(".diff")
    if diff_source.exists():
        shutil.copy2(diff_source, destination.with_suffix(".diff"))

    return {"success": True, "approved": False, "rejected_path": str(destination)}
