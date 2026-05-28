# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "patch-request"


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def create_patch_request(
    title: str,
    objective: str,
    context: str = "",
    source: str = "operator",
    priority: str = "normal",
    tags: Optional[List[str]] = None,
    related_files: Optional[List[str]] = None,
    root_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    if not title.strip():
        raise ValueError("Campo obrigatorio ausente: title")
    if not objective.strip():
        raise ValueError("Campo obrigatorio ausente: objective")

    base_root = Path(root_path) if root_path else ROOT
    requests_dir = base_root / "k_atlas" / "self_evolution" / "patch_requests"
    requests_dir.mkdir(parents=True, exist_ok=True)

    request_id = str(uuid.uuid4())
    created_at = now_iso()

    data = {
        "request_id": request_id,
        "title": title.strip(),
        "objective": objective.strip(),
        "context": context.strip(),
        "source": source.strip(),
        "priority": priority.strip().lower(),
        "tags": tags or [],
        "related_files": related_files or [],
        "status": "requested",
        "created_at": created_at,
        "updated_at": created_at,
        "governance": {
            "supervised": True,
            "requires_human_approval": True,
            "can_modify_code": False,
            "can_access_internet": False,
            "can_modify_core": False,
        },
    }

    filename = created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(title) + ".json"
    path = requests_dir / filename
    write_json_atomic(path, data)

    return {"success": True, "message": "Pedido de melhoria registrado.", "request": data, "path": str(path)}


def list_patch_requests(root_path: Optional[str | Path] = None, limit: int = 50) -> Dict[str, Any]:
    base_root = Path(root_path) if root_path else ROOT
    requests_dir = base_root / "k_atlas" / "self_evolution" / "patch_requests"
    requests_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for path in sorted(requests_dir.glob("*.json"))[-limit:]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {"error": str(exc)}
        items.append({"path": str(path), "data": data})

    return {"success": True, "total": len(items), "requests": items}


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--source", default="operator")
    parser.add_argument("--priority", default="normal")
    parser.add_argument("--tags", default="")
    parser.add_argument("--related-files", default="")
    args = parser.parse_args()

    result = create_patch_request(
        title=args.title,
        objective=args.objective,
        context=args.context,
        source=args.source,
        priority=args.priority,
        tags=parse_csv(args.tags),
        related_files=parse_csv(args.related_files),
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
