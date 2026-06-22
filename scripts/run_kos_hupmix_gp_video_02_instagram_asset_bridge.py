
from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
AUDIT_REPORT = ROOT / "reports" / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
ASSETS_INBOX = ROOT / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
RUNTIME = ROOT / "local_runtime" / "kos_hupmix_gp_video_02_instagram_asset_bridge"

ASSETS_INBOX.mkdir(parents=True, exist_ok=True)
RUNTIME.mkdir(parents=True, exist_ok=True)

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".webm"}

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def find_from_report():
    audit = read_json(AUDIT_REPORT)

    candidates = []

    direct_download = audit.get("download") or {}
    if direct_download.get("stored_path"):
        candidates.append(ROOT / direct_download.get("stored_path"))

    instagram = audit.get("instagram") or {}
    nested_download = instagram.get("download") or {}
    if nested_download.get("stored_path"):
        candidates.append(ROOT / nested_download.get("stored_path"))

    latest = audit.get("latest") or {}
    if latest.get("stored_path"):
        candidates.append(ROOT / latest.get("stored_path"))

    for item in candidates:
        if item.exists() and item.suffix.lower() in VIDEO_EXTS:
            return item

    return None

def find_latest_local_video():
    base = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix"
    if not base.exists():
        return None

    videos = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    if not videos:
        return None

    videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return videos[0]

def main():
    source = find_from_report() or find_latest_local_video()

    event = {
        "status": None,
        "created_at": datetime.now().isoformat(),
        "source": rel(source) if source else None,
        "target": None,
        "copied": False,
        "assets_inbox": rel(ASSETS_INBOX),
        "next_step": None
    }

    if not source:
        event["status"] = "KOS_HUPMIX_GP_VIDEO_02_INSTAGRAM_SOURCE_NOT_FOUND"
        event["next_step"] = "Rodar auditoria Instagram Hupmix novamente."
    else:
        target = ASSETS_INBOX / ("take_00_instagram_reference_" + source.name)

        if target.exists() and target.stat().st_size == source.stat().st_size:
            copied = False
        else:
            shutil.copy2(source, target)
            copied = True

        event["status"] = "KOS_HUPMIX_GP_VIDEO_02_INSTAGRAM_ASSET_BRIDGE_READY"
        event["target"] = rel(target)
        event["copied"] = copied
        event["next_step"] = "Rodar GP_VIDEO_02 Real Asset Audit usando o video baixado do Instagram como asset real inicial."

    status_path = RUNTIME / "status.json"
    status_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(event, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
