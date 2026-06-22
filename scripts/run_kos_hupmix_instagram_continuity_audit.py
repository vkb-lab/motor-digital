from pathlib import Path
from datetime import datetime
import json
import urllib.parse
import urllib.request
import re

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")
REPORTS = ROOT / "reports"
AUDIT_ROOT = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix"
TOKEN_PATH = ROOT / "local_runtime" / "kos_secrets" / "meta_access_token.txt"

REPORTS.mkdir(parents=True, exist_ok=True)
AUDIT_ROOT.mkdir(parents=True, exist_ok=True)

IG_USER_ID = "17841471706662294"
GRAPH_VERSION = "v20.0"

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = AUDIT_ROOT / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def safe_text(value):
    return str(value or "").strip()

def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "K-OS Hupmix read-only"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def download_url(url: str, path: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "K-OS Hupmix read-only"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())
    return path

def media_ext(media_type: str, url: str) -> str:
    mt = str(media_type or "").upper()
    u = str(url or "").lower()
    if "VIDEO" in mt or ".mp4" in u:
        return ".mp4"
    if ".png" in u:
        return ".png"
    if ".webp" in u:
        return ".webp"
    return ".jpg"

def analyze_video_local(path: Path):
    result = {
        "path": rel(path),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else 0,
        "analysis_status": "not_started",
        "frames_exported": []
    }

    if not path.exists():
        result["analysis_status"] = "missing"
        return result

    try:
        import imageio
        from PIL import Image, ImageDraw

        reader = imageio.get_reader(str(path))
        meta = {}
        try:
            meta = reader.get_meta_data()
        except Exception:
            meta = {}

        result["metadata"] = {
            "fps": meta.get("fps"),
            "duration": meta.get("duration"),
            "size": meta.get("size"),
            "nframes": meta.get("nframes"),
            "source_meta_keys": sorted([str(k) for k in meta.keys()])
        }

        frame_indexes = [0]
        fps = meta.get("fps") or 24
        duration = meta.get("duration") or 0
        if duration and duration > 2:
            frame_indexes = [0, int((duration * fps) / 2), max(0, int(duration * fps) - 2)]

        frame_paths = []
        for idx, frame_index in enumerate(frame_indexes):
            try:
                frame = reader.get_data(frame_index)
                img = Image.fromarray(frame).convert("RGB")
                img.thumbnail((360, 640))
                frame_path = path.with_name(path.stem + f"_frame_{idx+1}.jpg")
                img.save(frame_path, quality=88)
                frame_paths.append(rel(frame_path))
            except Exception:
                continue

        try:
            reader.close()
        except Exception:
            pass

        result["frames_exported"] = frame_paths
        result["analysis_status"] = "ok" if frame_paths else "metadata_only"
        return result

    except Exception as exc:
        result["analysis_status"] = "error"
        result["error"] = str(exc)
        return result

def analyze_image_local(path: Path):
    result = {
        "path": rel(path),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else 0,
        "analysis_status": "not_started"
    }

    if not path.exists():
        result["analysis_status"] = "missing"
        return result

    try:
        from PIL import Image
        img = Image.open(path)
        result["metadata"] = {
            "format": img.format,
            "mode": img.mode,
            "size": img.size
        }
        thumb = img.convert("RGB")
        thumb.thumbnail((720, 720))
        thumb_path = path.with_name(path.stem + "_thumb.jpg")
        thumb.save(thumb_path, quality=88)
        result["thumbnail"] = rel(thumb_path)
        result["analysis_status"] = "ok"
        return result
    except Exception as exc:
        result["analysis_status"] = "error"
        result["error"] = str(exc)
        return result

def score_gp_relevance(caption: str):
    text = caption.lower()
    keywords = [
        "oxy", "oxy power", "garoto oxy", "limpeza", "oxigenio ativo",
        "oxigênio ativo", "sem cloro", "5l", "5 litros", "49,90",
        "hupmix", "whatsapp"
    ]
    hits = [k for k in keywords if k in text]
    return {
        "score": len(hits),
        "hits": hits,
        "seems_gp_oxy_related": len(hits) >= 2 or "oxy" in text
    }

local_state = {
    "production_kit_json": {
        "path": "campaigns/hupmix_gp_recovery/GP_VIDEO_01_PRODUCTION_KIT.json",
        "exists": (ROOT / "campaigns/hupmix_gp_recovery/GP_VIDEO_01_PRODUCTION_KIT.json").exists()
    },
    "video_factory_job": {
        "path": "campaigns/hupmix_gp_recovery/GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json",
        "exists": (ROOT / "campaigns/hupmix_gp_recovery/GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json").exists()
    },
    "local_preview_mp4": {
        "path": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4",
        "exists": (ROOT / "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4").exists()
    },
    "local_storyboard": {
        "path": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_STORYBOARD.png",
        "exists": (ROOT / "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_STORYBOARD.png").exists()
    },
    "human_review_approval": {
        "path": "live/human_decision_center/hupmix_gp_video_01_publication_review_approval.json",
        "exists": (ROOT / "live/human_decision_center/hupmix_gp_video_01_publication_review_approval.json").exists()
    }
}

production_kit = read_json(ROOT / "campaigns/hupmix_gp_recovery/GP_VIDEO_01_PRODUCTION_KIT.json")
video_job = read_json(ROOT / "campaigns/hupmix_gp_recovery/GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json")

latest_payload = None
latest_item = None
download = None
download_analysis = None
fetch_status = "not_started"

if not TOKEN_PATH.exists():
    fetch_status = "META_TOKEN_NOT_FOUND"
elif not TOKEN_PATH.read_text(encoding="utf-8").strip():
    fetch_status = "META_TOKEN_EMPTY"
else:
    token = TOKEN_PATH.read_text(encoding="utf-8").strip()
    fields = "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url,children{media_type,media_url,thumbnail_url,permalink,timestamp}"
    params = urllib.parse.urlencode({
        "fields": fields,
        "limit": "5",
        "access_token": token
    })
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_USER_ID}/media?{params}"

    try:
        latest_payload = http_json(url)
        items = latest_payload.get("data", [])
        latest_item = items[0] if items else None
        fetch_status = "KOS_HUPMIX_INSTAGRAM_FETCH_READY" if latest_item else "KOS_HUPMIX_INSTAGRAM_NO_MEDIA_FOUND"
    except Exception as exc:
        fetch_status = "KOS_HUPMIX_INSTAGRAM_FETCH_ERROR"
        latest_payload = {"error": str(exc)}

if latest_item:
    media_candidates = []

    if latest_item.get("media_url"):
        media_candidates.append({
            "media_type": latest_item.get("media_type"),
            "url": latest_item.get("media_url"),
            "source": "latest.media_url"
        })

    if latest_item.get("thumbnail_url"):
        media_candidates.append({
            "media_type": "IMAGE_THUMBNAIL",
            "url": latest_item.get("thumbnail_url"),
            "source": "latest.thumbnail_url"
        })

    children = ((latest_item.get("children") or {}).get("data") or [])
    for child in children:
        if child.get("media_url") or child.get("thumbnail_url"):
            media_candidates.append({
                "media_type": child.get("media_type"),
                "url": child.get("media_url") or child.get("thumbnail_url"),
                "source": "latest.children"
            })

    if media_candidates:
        chosen = media_candidates[0]
        ext = media_ext(chosen.get("media_type"), chosen.get("url"))
        media_id = re.sub(r"[^a-zA-Z0-9_-]+", "_", safe_text(latest_item.get("id")) or "latest")
        media_path = RUN_DIR / f"{media_id}{ext}"

        try:
            download_url(chosen["url"], media_path)
            download = {
                "status": "KOS_HUPMIX_MEDIA_DOWNLOADED",
                "source": chosen["source"],
                "media_type": chosen.get("media_type"),
                "stored_path": rel(media_path),
                "size": media_path.stat().st_size
            }

            if ext == ".mp4":
                download_analysis = analyze_video_local(media_path)
            else:
                download_analysis = analyze_image_local(media_path)

        except Exception as exc:
            download = {
                "status": "KOS_HUPMIX_MEDIA_DOWNLOAD_ERROR",
                "error": str(exc),
                "source": chosen["source"],
                "media_type": chosen.get("media_type")
            }

local_preview_analysis = analyze_video_local(ROOT / "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")

caption = safe_text((latest_item or {}).get("caption"))
gp_score = score_gp_relevance(caption)

interpretation = {
    "where_project_stopped": None,
    "instagram_latest_status": None,
    "recommended_next_action": None,
    "requires_human_ok": True,
    "can_act_without_publish": True
}

if local_state["local_preview_mp4"]["exists"] and local_state["video_factory_job"]["exists"]:
    interpretation["where_project_stopped"] = "GP_VIDEO_01 possui preview MP4 local e job Video Factory. Proximo passo natural: comparar com Instagram Hupmix e registrar decisao humana."
else:
    interpretation["where_project_stopped"] = "Contexto local incompleto. K-OS deve pedir arquivos/anexos ou regenerar Video Factory antes de seguir."

if latest_item:
    if gp_score["seems_gp_oxy_related"]:
        interpretation["instagram_latest_status"] = "A ultima publicacao Hupmix parece relacionada ao GP/Oxy Power pelos termos da legenda."
        interpretation["recommended_next_action"] = "Abrir revisao Hupmix, validar a publicacao baixada e registrar OK humano antes de qualquer proxima campanha."
    else:
        interpretation["instagram_latest_status"] = "A ultima publicacao Hupmix nao parece claramente relacionada ao GP/Oxy Power pela legenda."
        interpretation["recommended_next_action"] = "Continuar GP_VIDEO_01 a partir do preview local, pedir assets reais se necessario e nao publicar sem OK humano."
else:
    interpretation["instagram_latest_status"] = "Nao foi possivel obter a ultima publicacao Hupmix via Meta Graph."
    interpretation["recommended_next_action"] = "Usar lousa local do GP_VIDEO_01 e solicitar link/anexo da publicacao ao operador."

report = {
    "status": "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT_READY",
    "created_at": datetime.now().isoformat(),
    "run_id": RUN_ID,
    "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_01 / Instagram",
    "policy": {
        "meta_graph_read_only": True,
        "no_scraping": True,
        "no_logged_browser_automation": True,
        "no_publish": True,
        "no_delete": True,
        "no_comment": True,
        "no_dm": True,
        "no_paid_ai": True,
        "human_gate_required": True
    },
    "local_state": local_state,
    "local_preview_analysis": local_preview_analysis,
    "instagram": {
        "fetch_status": fetch_status,
        "ig_user_id": IG_USER_ID,
        "latest_item": latest_item,
        "download": download,
        "download_analysis": download_analysis,
        "gp_relevance_from_caption": gp_score
    },
    "continuity": {
        "production_kit_loaded": production_kit is not None,
        "video_job_loaded": video_job is not None,
        "scene_count": len((video_job or {}).get("scenes", [])) if isinstance(video_job, dict) else 0,
        "campaign": "GP / Garoto Oxy Power / Oxy Power"
    },
    "interpretation": interpretation,
    "outputs": {
        "run_dir": rel(RUN_DIR),
        "json_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
        "md_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.md"
    }
}

json_path = REPORTS / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
md_path = REPORTS / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# K-OS Hupmix Instagram Continuity Audit")
md.append("")
md.append(f"Status: {report['status']}")
md.append("")
md.append("## Politica")
for k, v in report["policy"].items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Estado local")
for k, v in local_state.items():
    md.append(f"- {k}: {v.get('exists')} | {v.get('path')}")
md.append("")
md.append("## Instagram")
md.append(f"- fetch_status: {fetch_status}")
if latest_item:
    md.append(f"- media_type: {latest_item.get('media_type')}")
    md.append(f"- timestamp: {latest_item.get('timestamp')}")
    md.append(f"- permalink: {latest_item.get('permalink')}")
    md.append(f"- caption_score: {gp_score.get('score')}")
    md.append(f"- caption_hits: {', '.join(gp_score.get('hits', []))}")
if download:
    md.append(f"- download_status: {download.get('status')}")
    md.append(f"- download_path: {download.get('stored_path')}")
md.append("")
md.append("## Interpretacao")
for k, v in interpretation.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Proxima acao segura")
md.append(str(interpretation.get("recommended_next_action")))

md_path.write_text("\n".join(md), encoding="utf-8")

print(json.dumps({
    "status": report["status"],
    "fetch_status": fetch_status,
    "latest_media_type": (latest_item or {}).get("media_type"),
    "latest_timestamp": (latest_item or {}).get("timestamp"),
    "download": download,
    "local_preview_analysis_status": local_preview_analysis.get("analysis_status"),
    "gp_caption_score": gp_score,
    "recommended_next_action": interpretation.get("recommended_next_action"),
    "json_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
    "md_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.md",
    "run_dir": rel(RUN_DIR)
}, ensure_ascii=False, indent=2))
