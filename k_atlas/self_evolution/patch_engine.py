# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from k_atlas.self_evolution.diff_viewer import generate_file_diff, save_diff
from k_atlas.self_evolution.risk_analyzer import analyze_risk


ROOT = Path(__file__).resolve().parents[2]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "patch"


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def ensure_dirs(root_path: str | Path | None = None) -> Dict[str, Path]:
    base_root = Path(root_path) if root_path else ROOT
    base_dir = base_root / "k_atlas" / "self_evolution"
    paths = {
        "patch_inbox": base_dir / "patch_inbox",
        "snapshots": base_dir / "snapshots",
        "rollback": base_dir / "rollback",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def read_file_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def create_snapshot(target_file: str, root_path: str | Path | None = None, patch_id: Optional[str] = None) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    base_root = Path(root_path) if root_path else ROOT
    target_path = Path(target_file)
    if not target_path.is_absolute():
        target_path = base_root / target_path

    snapshot_id = str(uuid.uuid4())
    created_at = now_iso()
    data = {
        "snapshot_id": snapshot_id,
        "patch_id": patch_id,
        "target_file": str(target_path),
        "exists": target_path.exists(),
        "content": read_file_if_exists(target_path),
        "created_at": created_at,
        "purpose": "rollback_preparation",
    }

    path = paths["snapshots"] / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(target_path.name) + ".snapshot.json")
    write_json_atomic(path, data)
    return {"snapshot_id": snapshot_id, "snapshot_path": str(path), "target_file": str(target_path), "exists": target_path.exists()}


def create_rollback_plan(patch_id: str, snapshot: Dict[str, Any], root_path: str | Path | None = None) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    created_at = now_iso()
    data = {
        "rollback_id": str(uuid.uuid4()),
        "patch_id": patch_id,
        "snapshot": snapshot,
        "created_at": created_at,
        "can_auto_rollback": False,
        "requires_human_approval": True,
        "instructions": [
            "Abrir snapshot indicado.",
            "Revisar conteudo original.",
            "Restaurar manualmente apenas apos aprovacao humana.",
            "Rodar smoke tests e dev_runner.",
            "Commitar rollback se necessario.",
        ],
    }

    path = paths["rollback"] / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + patch_id + ".rollback.json")
    write_json_atomic(path, data)
    return {"rollback_path": str(path), "rollback": data}


def create_patch_proposal(
    title: str,
    objective: str,
    target_file: str,
    proposed_content: str,
    request_id: Optional[str] = None,
    author: str = "engineer",
    root_path: str | Path | None = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if not title.strip():
        raise ValueError("Campo obrigatorio ausente: title")
    if not objective.strip():
        raise ValueError("Campo obrigatorio ausente: objective")
    if not target_file.strip():
        raise ValueError("Campo obrigatorio ausente: target_file")

    paths = ensure_dirs(root_path)
    patch_id = str(uuid.uuid4())
    created_at = now_iso()

    diff_text = generate_file_diff(target_file=target_file, proposed_content=proposed_content, root_path=root_path)
    risk = analyze_risk(target_files=[target_file], proposed_content=proposed_content, patch_text=diff_text)
    snapshot = create_snapshot(target_file=target_file, root_path=root_path, patch_id=patch_id)
    rollback = create_rollback_plan(patch_id=patch_id, snapshot=snapshot, root_path=root_path)

    data = {
        "patch_id": patch_id,
        "request_id": request_id,
        "title": title.strip(),
        "objective": objective.strip(),
        "target_files": [target_file],
        "proposed_content": proposed_content,
        "diff": diff_text,
        "risk": risk,
        "snapshot": snapshot,
        "rollback": rollback,
        "author": author.strip(),
        "tags": tags or [],
        "status": "proposed_waiting_human_approval",
        "created_at": created_at,
        "updated_at": created_at,
        "governance": {
            "supervised": True,
            "requires_human_approval": True,
            "can_auto_apply": False,
            "destructive_changes_allowed": False,
        },
    }

    path = paths["patch_inbox"] / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(title) + ".json")
    diff_path = path.with_suffix(".diff")
    write_json_atomic(path, data)
    save_diff(diff_text, diff_path)

    return {
        "success": True,
        "message": "Proposta de patch criada em modo supervisionado.",
        "patch_id": patch_id,
        "patch_path": str(path),
        "diff_path": str(diff_path),
        "risk": risk,
        "snapshot": snapshot,
        "rollback_path": rollback["rollback_path"],
        "can_auto_apply": False,
    }


def list_patch_inbox(root_path: str | Path | None = None, limit: int = 50) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    items = []
    for path in sorted(paths["patch_inbox"].glob("*.json"))[-limit:]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {"error": str(exc)}
        items.append({"path": str(path), "data": data})
    return {"success": True, "total": len(items), "patches": items}


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--target-file", required=True)
    parser.add_argument("--proposed-content", required=True)
    parser.add_argument("--request-id", default=None)
    parser.add_argument("--author", default="engineer")
    parser.add_argument("--tags", default="")
    args = parser.parse_args()

    result = create_patch_proposal(
        title=args.title,
        objective=args.objective,
        target_file=args.target_file,
        proposed_content=args.proposed_content,
        request_id=args.request_id,
        author=args.author,
        tags=parse_csv(args.tags),
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
