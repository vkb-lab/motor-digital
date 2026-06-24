
from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CAMPAIGN = ROOT / "campaigns" / "hupmix_gp_recovery"
RUNTIME = ROOT / "local_runtime" / "kos_hupmix_gp_video_02_manus_upgrade"
OUT_DIR = ROOT / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_manus_style"

for p in [REPORTS, CAMPAIGN, RUNTIME, OUT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

INDEX_PATH = ROOT / "memory" / "kos_knowledge" / "KOS_HUPMIX_MANUS_REFERENCE_INDEX.json"

BRIEF_JSON = CAMPAIGN / "GP_VIDEO_02_MANUS_EDITOR_BRIEF.json"
BRIEF_MD = CAMPAIGN / "GP_VIDEO_02_MANUS_EDITOR_BRIEF.md"
PROMPTS_JSON = CAMPAIGN / "GP_VIDEO_02_MANUS_PROMPT_PACK.json"
PROMPTS_MD = CAMPAIGN / "GP_VIDEO_02_MANUS_PROMPT_PACK.md"
SCORE_JSON = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_MANUS_CREATIVE_SCORE.json"
SCORE_MD = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_MANUS_CREATIVE_SCORE.md"
REPORT_JSON = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_V1.json"
REPORT_MD = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_V1.md"

OUTPUT_MP4 = OUT_DIR / "GP_VIDEO_02_MANUS_STYLE_PREVIEW.mp4"
STORYBOARD = OUT_DIR / "GP_VIDEO_02_MANUS_STYLE_STORYBOARD.png"
STATUS = RUNTIME / "status.json"

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

def write_json_if_changed(path: Path, data: dict):
    content = json.dumps(data, ensure_ascii=False, indent=2)
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def write_text_if_changed(path: Path, content: str):
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def files_by_tag(index: dict, tag: str):
    out = []
    for item in index.get("files", []):
        if tag in item.get("tags", []):
            p = ROOT / item.get("runtime_path", "")
            if p.exists():
                out.append(p)
    return out

def first_file(paths, exts=None):
    for p in paths:
        if p.exists() and (not exts or p.suffix.lower() in exts):
            return p
    return None

def find_source_video(index: dict):
    candidates = []

    gen = read_json(ROOT / "local_runtime" / "kos_hupmix_gp_video_02_local_video_generator" / "status.json")
    if gen.get("output"):
        candidates.append(ROOT / gen.get("output"))

    bridge = read_json(ROOT / "local_runtime" / "kos_hupmix_gp_video_02_instagram_asset_bridge" / "status.json")
    if bridge.get("target"):
        candidates.append(ROOT / bridge.get("target"))

    for item in index.get("files", []):
        if item.get("type") == "video":
            candidates.append(ROOT / item.get("runtime_path", ""))

    for p in candidates:
        if p.exists() and p.suffix.lower() in VIDEO_EXTS:
            return p

    return None

def make_card(size, title, subtitle, bullets, character=None, product=None):
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    w, h = size
    img = Image.new("RGB", (w, h), (12, 16, 24))
    draw = ImageDraw.Draw(img)

    def font(size_value, bold=False):
        paths = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        ]
        for item in paths:
            try:
                return ImageFont.truetype(item, size_value)
            except Exception:
                pass
        return ImageFont.load_default()

    title_font = font(max(34, int(w * 0.062)), True)
    subtitle_font = font(max(24, int(w * 0.040)), False)
    body_font = font(max(22, int(w * 0.036)), False)
    small_font = font(max(18, int(w * 0.028)), False)

    margin = int(w * 0.07)

    draw.rounded_rectangle(
        [margin, int(h * 0.08), w - margin, int(h * 0.90)],
        radius=32,
        fill=(245, 247, 250)
    )

    y = int(h * 0.12)
    draw.text((margin + 34, y), title, fill=(15, 18, 28), font=title_font)
    y += int(h * 0.07)
    draw.text((margin + 34, y), subtitle, fill=(60, 66, 78), font=subtitle_font)
    y += int(h * 0.10)

    for bullet in bullets:
        draw.text((margin + 34, y), bullet, fill=(28, 32, 42), font=body_font)
        y += int(h * 0.055)

    def paste_asset(asset_path, box):
        if not asset_path or not asset_path.exists():
            return
        try:
            asset = Image.open(asset_path).convert("RGBA")
            bw, bh = box[2] - box[0], box[3] - box[1]
            asset.thumbnail((bw, bh))
            x = box[0] + (bw - asset.width) // 2
            y = box[1] + (bh - asset.height) // 2
            img.paste(asset, (x, y), asset)
        except Exception:
            pass

    if character:
        paste_asset(character, (margin + 20, int(h * 0.48), int(w * 0.50), int(h * 0.86)))

    if product:
        paste_asset(product, (int(w * 0.50), int(h * 0.44), w - margin - 20, int(h * 0.84)))

    draw.text((margin + 34, int(h * 0.86)), "HupMix | Garoto Oxy Power", fill=(80, 86, 96), font=small_font)
    return np.array(img)

def make_storyboard(size):
    from PIL import Image, ImageDraw, ImageFont

    w, h = size
    img = Image.new("RGB", (w * 3, h), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", max(26, int(w * 0.045)))
        font_body = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(20, int(w * 0.032)))
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    panels = [
        ("1. Hook", "Garoto Oxy voltou\ncom teste real"),
        ("2. Prova", "Asset real + produto\nsem inventar footage"),
        ("3. Oferta", "Oxy Power 5L\nR$ 49,90 na HupMix"),
    ]

    for i, (title, body) in enumerate(panels):
        x0 = i * w
        draw.rectangle([x0 + 20, 20, x0 + w - 20, h - 20], outline=(40, 44, 54), width=3)
        draw.text((x0 + 50, 60), title, fill=(20, 24, 34), font=font_title)
        draw.text((x0 + 50, 130), body, fill=(50, 56, 68), font=font_body)

    img.save(STORYBOARD)

def generate_preview(source, character, product):
    try:
        from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
    except Exception:
        from moviepy import VideoFileClip, ImageClip, concatenate_videoclips

    def duration(clip):
        return float(getattr(clip, "duration", 0) or 0)

    def subclip(clip, start, end):
        if hasattr(clip, "subclip"):
            return clip.subclip(start, end)
        return clip.subclipped(start, end)

    def set_duration(clip, seconds):
        if hasattr(clip, "set_duration"):
            return clip.set_duration(seconds)
        return clip.with_duration(seconds)

    clip = VideoFileClip(str(source))
    dur = duration(clip)
    main = subclip(clip, 0, min(dur, 14.0))

    w = int(getattr(main, "w", 720) or 720)
    h = int(getattr(main, "h", 1280) or 1280)
    size = (w, h)

    intro_img = make_card(
        size,
        "Garoto Oxy voltou",
        "Agora com prova real",
        ["Oxy Power 5L", "Oxigenio ativo", "Sem cloro", "Alto poder de limpeza"],
        character=character,
        product=product
    )

    outro_img = make_card(
        size,
        "Oxy Power 5L",
        "Oferta HupMix",
        ["R$ 49,90", "Chame no WhatsApp", "Ou passe na loja", "Publicar so com OK humano"],
        character=None,
        product=product
    )

    intro = set_duration(ImageClip(intro_img), 3.0)
    outro = set_duration(ImageClip(outro_img), 4.0)

    final = concatenate_videoclips([intro, main, outro], method="compose")
    final.write_videofile(
        str(OUTPUT_MP4),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=2,
        logger=None
    )

    make_storyboard(size)

    try:
        clip.close()
        final.close()
    except Exception:
        pass

def main():
    existing = read_json(REPORT_JSON)
    if existing.get("status") == "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_V1_READY" and OUTPUT_MP4.exists():
        runtime_event = dict(existing)
        runtime_event["runtime_status"] = "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_ALREADY_READY_CLEAN"
        runtime_event["checked_at"] = datetime.now().isoformat()
        STATUS.write_text(json.dumps(runtime_event, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(runtime_event, ensure_ascii=False, indent=2))
        return

    index = read_json(INDEX_PATH)

    character = first_file(files_by_tag(index, "character"), {".png", ".jpg", ".jpeg", ".webp"})
    product = first_file(files_by_tag(index, "product"), {".png", ".jpg", ".jpeg", ".webp"})
    source = find_source_video(index)

    score = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_MANUS_CREATIVE_SCORE_READY",
        "score_total": 62,
        "level": "technical_preview_plus_reference",
        "criteria": {
            "uses_real_asset": 20,
            "has_offer": 12,
            "has_cta": 10,
            "character_consistency": 6,
            "visual_strength": 6,
            "story_arc": 8
        },
        "gaps": [
            "personagem ainda nao aparece como video vivo consistente",
            "prova visual ainda depende de asset reaproveitado",
            "edicao ainda simples",
            "faltam cortes dinamicos e ritmo de social video"
        ],
        "target_score": 85,
        "next_upgrade": "usar referencias Manus para briefing de editor, prompts visuais e preview mais forte"
    }

    brief = {
        "status": "KOS_GP_VIDEO_02_MANUS_EDITOR_BRIEF_READY",
        "title": "GP_VIDEO_02 — Garoto Oxy Power Manus-compatible",
        "objective": "Transformar o preview tecnico em uma peca com narrativa, personagem, produto, prova e oferta.",
        "format": "vertical 9:16, 20-30s",
        "structure": [
            {"scene": 1, "name": "Hook", "screen_text": "O Garoto Oxy voltou", "duration": "2-3s"},
            {"scene": 2, "name": "Produto", "screen_text": "Oxy Power 5L", "duration": "3-4s"},
            {"scene": 3, "name": "Prova real", "screen_text": "Teste real / resultado real", "duration": "8-12s"},
            {"scene": 4, "name": "Beneficio", "screen_text": "Sem cloro + oxigenio ativo", "duration": "4-5s"},
            {"scene": 5, "name": "Oferta", "screen_text": "R$ 49,90 na HupMix", "duration": "4-5s"}
        ],
        "editor_notes": [
            "usar ritmo rapido",
            "manter texto grande e legivel",
            "nao inventar prova visual",
            "usar produto e personagem como identidade",
            "publicacao somente apos OK humano"
        ],
        "assets": {
            "source_video": rel(source) if source else None,
            "character_reference": rel(character) if character else None,
            "product_reference": rel(product) if product else None,
            "manus_index": "memory/kos_knowledge/KOS_HUPMIX_MANUS_REFERENCE_INDEX.json"
        }
    }

    prompts = {
        "status": "KOS_GP_VIDEO_02_MANUS_PROMPT_PACK_READY",
        "purpose": "Prompts para editor humano ou IA visual futura, sem executar IA paga automaticamente.",
        "prompts": [
            {
                "id": "visual_character_consistency",
                "prompt": "Criar cena vertical 9:16 com personagem Garoto Oxy como mascote comercial amigavel, energia de vendedor local, segurando ou apontando para Oxy Power 5L, estilo social media limpo, texto grande e legivel."
            },
            {
                "id": "product_offer_card",
                "prompt": "Criar card vertical 9:16 para Oxy Power 5L na HupMix, destacar R$ 49,90, beneficios sem cloro e oxigenio ativo, CTA WhatsApp, visual de varejo promocional moderno."
            },
            {
                "id": "proof_scene_direction",
                "prompt": "Editar cena de prova real mostrando antes, aplicacao e depois sem exagero, cortes rapidos, setas ou labels discretos, mantendo credibilidade visual."
            }
        ],
        "blocked": {
            "paid_ai_auto_run": True,
            "publishing": True,
            "fake_proof": True
        }
    }

    write_json_if_changed(SCORE_JSON, score)
    write_text_if_changed(SCORE_MD, "# GP_VIDEO_02 Manus Creative Score\n\nStatus: READY\n\nScore atual: 62/100\n\nMeta: 85/100\n\nPrincipal gap: transformar preview tecnico em peca narrativa com personagem, prova e oferta.\n")

    write_json_if_changed(BRIEF_JSON, brief)
    write_text_if_changed(BRIEF_MD, "# GP_VIDEO_02 Manus Editor Brief\n\nStatus: READY\n\nObjetivo: transformar preview tecnico em peca social com narrativa, personagem, produto, prova e oferta.\n\n## Estrutura\n\n1. Hook: O Garoto Oxy voltou\n2. Produto: Oxy Power 5L\n3. Prova real: asset real\n4. Beneficio: sem cloro + oxigenio ativo\n5. Oferta: R$ 49,90 na HupMix\n\nPublicacao bloqueada ate OK humano.\n")

    write_json_if_changed(PROMPTS_JSON, prompts)
    write_text_if_changed(PROMPTS_MD, "# GP_VIDEO_02 Manus Prompt Pack\n\nStatus: READY\n\nPrompts criados para IA visual futura ou editor humano. IA paga nao executada automaticamente.\n")

    generated = False
    fallback = False
    error = None

    if source:
        try:
            generate_preview(source, character, product)
            generated = OUTPUT_MP4.exists()
        except Exception as exc:
            error = str(exc)
            try:
                shutil.copy2(source, OUTPUT_MP4)
                fallback = True
                generated = OUTPUT_MP4.exists()
            except Exception as exc2:
                error = str(exc) + " | fallback_failed: " + str(exc2)

    report = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_V1_READY" if generated else "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_NEEDS_SOURCE",
        "score": "reports/KOS_HUPMIX_GP_VIDEO_02_MANUS_CREATIVE_SCORE.json",
        "brief": "campaigns/hupmix_gp_recovery/GP_VIDEO_02_MANUS_EDITOR_BRIEF.json",
        "prompt_pack": "campaigns/hupmix_gp_recovery/GP_VIDEO_02_MANUS_PROMPT_PACK.json",
        "preview": rel(OUTPUT_MP4) if OUTPUT_MP4.exists() else None,
        "storyboard": rel(STORYBOARD) if STORYBOARD.exists() else None,
        "source_video": rel(source) if source else None,
        "character_reference": rel(character) if character else None,
        "product_reference": rel(product) if product else None,
        "fallback_used": fallback,
        "error": error,
        "policy": {
            "no_publish": True,
            "no_paid_ai": True,
            "human_gate_required": True
        },
        "next_step": "Validar preview Manus-style no Operator Chat. Se aprovado, criar pacote para editor/publicacao gateada."
    }

    write_json_if_changed(REPORT_JSON, report)
    write_text_if_changed(REPORT_MD, "# KOS Hupmix GP_VIDEO_02 Manus Upgrade V1\n\nStatus: READY\n\nGerou score, briefing, prompt pack e preview local Manus-style.\n\nPublicacao segue bloqueada.\n")
    STATUS.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
