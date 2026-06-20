from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LATEST_STRATEGY = ROOT / "local_runtime" / "kos_social_ops" / "latest_social_strategy.json"
OUT_DIR = ROOT / "local_runtime" / "kos_social_ops" / "readiness"
LATEST_READINESS = OUT_DIR / "latest_publish_readiness.json"

REQUIRED_PATHS = [
    "reports/KOS_PHASE69D_HUPMIX_INSTAGRAM_AUDIT_BOOTSTRAP.json",
    "reports/KOS_PHASE69E_PUBLISH_AUDIT_GATE_BOOTSTRAP.json",
    "reports/KOS_PHASE69F_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_GATE_BOOTSTRAP.json",
    "reports/KOS_PHASE69G_REAL_PUBLISH_APPROVAL_LEDGER_BOOTSTRAP.json",
    "reports/KOS_PHASE69H_HUPMIX_REAL_PUBLISH_EXECUTOR_BOOTSTRAP.json",
    "scripts/run_phase69h_hupmix_real_publish_executor.py",
]

BLOCKED_TARGETS = {"paradaatlantida", "parada_atlantida", "17841480166187766", "869334472930140"}
ALLOWED_TARGETS = {"hupmix"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    return value.strip("-")[:100] or "readiness"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def valid_https_asset(asset_url: str) -> bool:
    return asset_url.startswith("https://") and len(asset_url.strip()) >= 12


def valid_caption(caption: str) -> bool:
    caption = caption.strip()
    return 10 <= len(caption) <= 2200


def check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": detail}


def build_readiness(target: str, asset_url: str, caption: str, readiness_id: str = "") -> dict[str, Any]:
    target_norm = target.strip().lower()
    readiness_id = slug(readiness_id or f"{target_norm}-readiness-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    strategy = read_json(LATEST_STRATEGY)

    path_status = []
    for rel in REQUIRED_PATHS:
        path_status.append({
            "path": rel,
            "exists": (ROOT / rel).exists(),
        })

    checks = [
        check("target_hupmix_only", target_norm == "hupmix" and target_norm in ALLOWED_TARGETS, f"target={target_norm}"),
        check("parada_atlantida_blocked", target_norm not in BLOCKED_TARGETS, "Parada Atlantida permanece bloqueada"),
        check("existing_publish_path_69d_69h_exists", all(item["exists"] for item in path_status), "Reutiliza caminho existente 69D-69H"),
        check("strategy_71b_exists", strategy.get("status") == "KOS_SOCIAL_STRATEGY_READY", f"strategy_status={strategy.get('status')}"),
        check("asset_https_public_syntax", valid_https_asset(asset_url), "asset_url deve ser HTTPS publico"),
        check("caption_valid", valid_caption(caption), "caption deve ter entre 10 e 2200 caracteres"),
        check("human_approval_required", True, "Publicacao real exige confirmacao humana"),
        check("no_new_publish_executor", True, "71C nao cria executor novo"),
        check("no_publish_call_executed", True, "Nenhum endpoint de publicacao foi chamado"),
    ]

    ready = all(item["ok"] for item in checks)

    result = {
        "status": "KOS_SOCIAL_PUBLISH_READINESS_READY_FOR_HUMAN_REVIEW" if ready else "KOS_SOCIAL_PUBLISH_READINESS_NOT_READY",
        "phase": "71C",
        "readiness_id": readiness_id,
        "target": target_norm,
        "asset_url": asset_url,
        "caption": caption,
        "strategy_status": strategy.get("status"),
        "checks": checks,
        "required_path_status": path_status,
        "existing_publish_path_reused": "69D-69E-69F-69G-69H",
        "creates_new_publish_executor": False,
        "publish_executor_reference": "scripts/run_phase69h_hupmix_real_publish_executor.py",
        "next_safe_step": "review_dashboard_then_use_existing_69F_69G_69H_gates",
        "auto_publish_enabled": False,
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "human_confirmation_required": True,
        "browser_scraping_enabled": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_locked": True,
        "parada_atlantida_locked": True,
        "instagram_publish_executed": False,
        "publish_endpoint_called": False,
        "http_post_used": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    result["readiness_sha256"] = sha256_text(json.dumps(result, ensure_ascii=False, sort_keys=True))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{readiness_id}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    LATEST_READINESS.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    result["path"] = str(out_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--asset-url", default="")
    parser.add_argument("--caption", default="")
    parser.add_argument("--readiness-id", default="")
    args = parser.parse_args()

    result = build_readiness(
        target=args.target,
        asset_url=args.asset_url,
        caption=args.caption,
        readiness_id=args.readiness_id,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
