from pathlib import Path
from datetime import datetime
import json
import textwrap
import math

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")
OUT_DIR = ROOT / "local_runtime" / "kos_video_previews" / "hupmix"
CAMPAIGN_DIR = ROOT / "campaigns" / "hupmix_gp_recovery"
REPORTS_DIR = ROOT / "reports"

OUT_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MP4_PATH = OUT_DIR / "GP_VIDEO_01_PREVIEW.mp4"
STORYBOARD_PATH = OUT_DIR / "GP_VIDEO_01_STORYBOARD.png"
JOB_PATH = CAMPAIGN_DIR / "GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json"
REPORT_JSON = REPORTS_DIR / "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1.json"
REPORT_MD = REPORTS_DIR / "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1.md"

WIDTH = 720
HEIGHT = 1280
FPS = 24

scenes = [
    {
        "title": "A solucao que faltava",
        "duration": 4,
        "speaker": "Garoto Oxy",
        "line": "A solucao que faltava para a limpeza da sua casa chegou.",
        "screen": "Oxy Power 5L na HupMix"
    },
    {
        "title": "Problema real",
        "duration": 5,
        "speaker": "Garoto Oxy",
        "line": "Sujeira no piso, gordura na cozinha ou box embacado? O Oxy Power ajuda.",
        "screen": "Antes da limpeza"
    },
    {
        "title": "Aplicacao",
        "duration": 6,
        "speaker": "Garoto Oxy",
        "line": "Ele usa Oxigenio Ativo para limpar de forma pratica, sem cloro e sem toxicidade.",
        "screen": "Aplicar, espalhar e limpar"
    },
    {
        "title": "Resultado",
        "duration": 6,
        "speaker": "Garoto Oxy",
        "line": "Olha a diferenca. E limpeza forte para o dia a dia.",
        "screen": "Antes e depois"
    },
    {
        "title": "Oferta e chamada",
        "duration": 6,
        "speaker": "Garoto Oxy",
        "line": "Oxy Power 5 litros por R$ 49,90. Passe na HupMix ou chame no WhatsApp.",
        "screen": "R$ 49,90 | Chame no WhatsApp"
    },
]

job = {
    "status": "KOS_VIDEO_FACTORY_FREE_MODE_JOB_READY",
    "created_at": datetime.now().isoformat(),
    "job_id": "hupmix_gp_video_01_free_mode_v1",
    "brand": "Hupmix",
    "campaign": "GP / Garoto Oxy Power / Oxy Power",
    "video_id": "GP_VIDEO_01",
    "mode": "free_local_render",
    "output_type": "mp4",
    "aspect_ratio": "9:16",
    "paid_ai_required": False,
    "provider_call_executed": False,
    "instagram_publish_executed": False,
    "human_gate_required": True,
    "scenes": scenes,
    "outputs": {
        "mp4": str(MP4_PATH.relative_to(ROOT)).replace("\\", "/"),
        "storyboard": str(STORYBOARD_PATH.relative_to(ROOT)).replace("\\", "/")
    }
}

JOB_PATH.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import imageio
except Exception as exc:
    raise SystemExit(f"Dependencia local ausente: {exc}")

def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_H1 = font(54, True)
FONT_H2 = font(38, True)
FONT_BODY = font(32, False)
FONT_SMALL = font(24, False)
FONT_PRICE = font(62, True)

def wrap(draw, text, fnt, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        box = draw.textbbox((0, 0), test, font=fnt)
        if box[2] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_center(draw, text, y, fnt, fill, max_width, spacing=8):
    lines = wrap(draw, text, fnt, max_width)
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (box[3] - box[1]) + spacing
    return y

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def make_frame(scene, scene_index, t, total_t):
    img = Image.new("RGB", (WIDTH, HEIGHT), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    progress = min(max(t / max(total_t, 0.01), 0), 1)

    # background bands
    draw.rectangle((0, 0, WIDTH, 190), fill=(22, 108, 74))
    draw.rectangle((0, 190, WIDTH, HEIGHT), fill=(247, 249, 248))
    draw.rectangle((0, HEIGHT - 160, WIDTH, HEIGHT), fill=(22, 108, 74))

    # header
    draw.text((42, 42), "HupMix", font=FONT_H1, fill=(255, 255, 255))
    draw.text((42, 110), "GP_VIDEO_01 | Garoto Oxy", font=FONT_SMALL, fill=(226, 245, 235))

    # progress bar
    draw.rectangle((42, 165, WIDTH - 42, 176), fill=(180, 210, 195))
    draw.rectangle((42, 165, int(42 + (WIDTH - 84) * progress), 176), fill=(255, 255, 255))

    # product card
    card_y = 245
    rounded_rect(draw, (70, card_y, WIDTH - 70, card_y + 330), 36, fill=(255, 255, 255), outline=(218, 228, 222), width=3)

    # product bottle mock
    bottle_x = WIDTH // 2 - 90
    bottle_y = card_y + 45
    rounded_rect(draw, (bottle_x, bottle_y, bottle_x + 180, bottle_y + 235), 28, fill=(230, 245, 238), outline=(21, 118, 76), width=5)
    rounded_rect(draw, (bottle_x + 45, bottle_y - 28, bottle_x + 135, bottle_y + 18), 12, fill=(21, 118, 76))
    draw.text((bottle_x + 34, bottle_y + 65), "OXY", font=FONT_H2, fill=(21, 118, 76))
    draw.text((bottle_x + 30, bottle_y + 112), "POWER", font=FONT_H2, fill=(21, 118, 76))
    draw.text((bottle_x + 62, bottle_y + 170), "5L", font=FONT_PRICE, fill=(19, 72, 50))

    # scene body
    y = 620
    y = draw_center(draw, scene["title"], y, FONT_H1, (20, 60, 45), WIDTH - 110, spacing=10)
    y += 25
    y = draw_center(draw, scene["line"], y, FONT_BODY, (35, 45, 50), WIDTH - 110, spacing=10)

    # screen tag
    rounded_rect(draw, (70, 970, WIDTH - 70, 1060), 24, fill=(232, 241, 236), outline=(210, 225, 216), width=2)
    draw_center(draw, scene["screen"], 995, FONT_SMALL, (20, 90, 65), WIDTH - 130, spacing=4)

    # price/CTA scene emphasis
    if scene_index == len(scenes) - 1:
        rounded_rect(draw, (120, 865, WIDTH - 120, 945), 28, fill=(255, 241, 190), outline=(225, 190, 90), width=3)
        draw_center(draw, "R$ 49,90", 875, FONT_PRICE, (85, 65, 10), WIDTH - 200)

    # footer
    draw.text((42, HEIGHT - 118), "Passe na HupMix ou chame no WhatsApp", font=FONT_SMALL, fill=(255, 255, 255))
    draw.text((42, HEIGHT - 78), "Preview local | Sem IA paga | Sem publicacao", font=FONT_SMALL, fill=(226, 245, 235))

    # small motion overlay
    pulse = int(18 * math.sin(progress * math.pi))
    draw.ellipse((WIDTH - 105 - pulse, 54 - pulse, WIDTH - 55 + pulse, 104 + pulse), outline=(255, 255, 255), width=4)

    return img

frames = []
story_tiles = []

for i, scene in enumerate(scenes):
    total_frames = scene["duration"] * FPS
    for f in range(total_frames):
        frames.append(np.array(make_frame(scene, i, f, total_frames)))
    story_tiles.append(make_frame(scene, i, total_frames - 1, total_frames).resize((216, 384)))

# Write MP4 with imageio ffmpeg backend
imageio.mimsave(str(MP4_PATH), frames, fps=FPS, macro_block_size=16)

# Storyboard
story = Image.new("RGB", (216 * len(story_tiles), 384), (255, 255, 255))
for idx, tile in enumerate(story_tiles):
    story.paste(tile, (idx * 216, 0))
story.save(STORYBOARD_PATH)

report = {
    "status": "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1_READY",
    "created_at": datetime.now().isoformat(),
    "job": str(JOB_PATH.relative_to(ROOT)).replace("\\", "/"),
    "outputs": {
        "mp4": str(MP4_PATH.relative_to(ROOT)).replace("\\", "/"),
        "mp4_size": MP4_PATH.stat().st_size,
        "storyboard": str(STORYBOARD_PATH.relative_to(ROOT)).replace("\\", "/"),
        "storyboard_size": STORYBOARD_PATH.stat().st_size,
    },
    "policy": {
        "no_ai_connected": True,
        "no_api_key_used": True,
        "no_paid_ai_executed": True,
        "no_publish": True,
        "no_deploy": True,
        "human_gate_required": True
    },
    "next_step": "Abrir Operator Chat e validar preview MP4 na lousa."
}

REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

REPORT_MD.write_text(
    "# K-OS Hupmix GP Video Factory Free Mode V1\n\n"
    "Status: preview MP4 local renderizado sem IA paga.\n\n"
    f"- Job: {report['job']}\n"
    f"- MP4: {report['outputs']['mp4']} | {report['outputs']['mp4_size']} bytes\n"
    f"- Storyboard: {report['outputs']['storyboard']} | {report['outputs']['storyboard_size']} bytes\n"
    "- Publicacao: bloqueada\n"
    "- IA paga: nao usada\n"
    "- Gate humano: obrigatorio\n",
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=True, indent=2))
