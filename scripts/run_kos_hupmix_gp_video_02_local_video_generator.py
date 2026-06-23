
from pathlib import Path
from datetime import datetime
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
RUNTIME = ROOT / "local_runtime" / "kos_hupmix_gp_video_02_local_video_generator"
OUT_DIR = ROOT / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_generated"

RUNTIME.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

STATUS_PATH = RUNTIME / "status.json"
OUTPUT_MP4 = OUT_DIR / "GP_VIDEO_02_GENERATED.mp4"
SCRIPT_JSON = OUT_DIR / "GP_VIDEO_02_GENERATED_SCRIPT.json"

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

def find_source_video():
    bridge = read_json(ROOT / "local_runtime" / "kos_hupmix_gp_video_02_instagram_asset_bridge" / "status.json")
    target = bridge.get("target")
    if target:
        p = ROOT / target
        if p.exists() and p.suffix.lower() in VIDEO_EXTS:
            return p

    videos = [p for p in ASSETS.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    if videos:
        videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return videos[0]

    base = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix"
    if base.exists():
        videos = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
        if videos:
            videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return videos[0]

    return None

def make_card(size, title, lines):
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    w, h = size
    img = Image.new("RGB", (w, h), (18, 20, 28))
    draw = ImageDraw.Draw(img)

    def font(size_value, bold=False):
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        ]
        for item in candidates:
            try:
                return ImageFont.truetype(item, size_value)
            except Exception:
                pass
        return ImageFont.load_default()

    title_font = font(max(40, int(w * 0.065)), True)
    body_font = font(max(28, int(w * 0.043)), False)
    small_font = font(max(22, int(w * 0.032)), False)

    margin = int(w * 0.08)
    y = int(h * 0.18)

    draw.rounded_rectangle(
        [margin, y - 40, w - margin, int(h * 0.82)],
        radius=28,
        fill=(245, 247, 250)
    )

    y += 20
    draw.text((margin + 36, y), title, fill=(18, 20, 28), font=title_font)
    y += int(h * 0.12)

    for line in lines:
        draw.text((margin + 36, y), line, fill=(32, 36, 44), font=body_font)
        y += int(h * 0.072)

    draw.text((margin + 36, int(h * 0.76)), "HupMix | Oxy Power 5L", fill=(80, 86, 96), font=small_font)
    return np.array(img)

def generate_with_moviepy(source: Path):
    import numpy as np

    try:
        from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
    except Exception:
        from moviepy import VideoFileClip, ImageClip, concatenate_videoclips

    def duration_of(clip):
        return float(getattr(clip, "duration", 0) or 0)

    def set_duration(clip, duration):
        if hasattr(clip, "set_duration"):
            return clip.set_duration(duration)
        return clip.with_duration(duration)

    def subclip(clip, start, end):
        if hasattr(clip, "subclip"):
            return clip.subclip(start, end)
        return clip.subclipped(start, end)

    def without_audio(clip):
        if hasattr(clip, "without_audio"):
            return clip.without_audio()
        return clip

    source_clip = VideoFileClip(str(source))
    dur = duration_of(source_clip)
    if dur <= 0:
        raise RuntimeError("video fonte sem duracao valida")

    end = min(dur, 18.0)
    main_clip = subclip(source_clip, 0, end)

    w = int(getattr(main_clip, "w", 1080) or 1080)
    h = int(getattr(main_clip, "h", 1920) or 1920)
    size = (w, h)

    intro_img = make_card(size, "Garoto Oxy voltou", [
        "Teste real com Oxy Power",
        "Sem cloro",
        "Oxigenio ativo",
        "Alto poder de limpeza"
    ])

    outro_img = make_card(size, "Oxy Power 5L", [
        "R$ 49,90",
        "Na HupMix",
        "Chame no WhatsApp",
        "Ou passe na loja"
    ])

    intro = set_duration(ImageClip(intro_img), 3.0)
    outro = set_duration(ImageClip(outro_img), 4.0)

    final = concatenate_videoclips([intro, main_clip, outro], method="compose")

    final.write_videofile(
        str(OUTPUT_MP4),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=2,
        logger=None
    )

    try:
        source_clip.close()
        final.close()
    except Exception:
        pass

def fallback_copy(source: Path):
    shutil.copy2(source, OUTPUT_MP4)

def main():
    source = find_source_video()

    script_payload = {
        "title": "GP_VIDEO_02 Gerado Localmente",
        "source": rel(source) if source else None,
        "structure": [
            "card_abertura_garoto_oxy",
            "trecho_real_instagram_asset",
            "card_oferta_oxy_power_5l_4990"
        ],
        "caption_suggestion": "O Garoto Oxy voltou em teste real. Oxy Power 5L com oxigenio ativo, sem cloro e por R$ 49,90 na HupMix. Chama no WhatsApp ou passa na loja.",
        "publication_policy": "BLOCKED_UNTIL_HUMAN_OK"
    }

    event = {
        "status": None,
        "created_at": datetime.now().isoformat(),
        "source": rel(source) if source else None,
        "output": rel(OUTPUT_MP4),
        "script": rel(SCRIPT_JSON),
        "generator": "moviepy_local_free_mode",
        "fallback_used": False,
        "policy": {
            "no_publish": True,
            "no_paid_ai": True,
            "human_gate_required": True
        },
        "next_step": None
    }

    if not source:
        event["status"] = "KOS_HUPMIX_GP_VIDEO_02_GENERATOR_WAITING_FOR_SOURCE"
        event["next_step"] = "Rodar Instagram Asset Bridge ou anexar um video real."
    else:
        try:
            generate_with_moviepy(source)
            event["status"] = "KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED"
            event["next_step"] = "Validar video gerado no Operator Chat e registrar OK humano."
        except Exception as exc:
            fallback_copy(source)
            event["status"] = "KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED_FALLBACK_COPY"
            event["fallback_used"] = True
            event["error"] = str(exc)
            event["next_step"] = "Validar copia operacional. Gerador local caiu em fallback."

    SCRIPT_JSON.write_text(json.dumps(script_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    STATUS_PATH.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(event, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
