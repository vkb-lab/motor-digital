
from pathlib import Path
from datetime import datetime
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local_runtime" / "kos_video_previews" / "hupmix"
REPORTS = ROOT / "reports"
CAMPAIGN = ROOT / "campaigns" / "hupmix_gp_recovery"

OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(exist_ok=True)
CAMPAIGN.mkdir(parents=True, exist_ok=True)

AUDIT = REPORTS / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
JOB = CAMPAIGN / "GP_VIDEO_02_CONTINUITY_FACTORY_JOB.json"
MP4 = OUT / "GP_VIDEO_02_CONTINUITY_PREVIEW.mp4"
STORYBOARD = OUT / "GP_VIDEO_02_CONTINUITY_STORYBOARD.png"

WIDTH = 720
HEIGHT = 1280
FPS = 24

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

audit = read_json(AUDIT) or {}
instagram = audit.get("instagram", {})
latest = instagram.get("latest_item") or {}
download = instagram.get("download") or {}
gp_score = instagram.get("gp_relevance_from_caption") or {}

reference_path = None
if download.get("stored_path"):
    p = ROOT / download.get("stored_path")
    if p.exists():
        reference_path = p

try:
    import imageio
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except Exception as exc:
    raise SystemExit(f"Dependencia local ausente: {exc}")

def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

F_H1 = font(52, True)
F_H2 = font(36, True)
F_BODY = font(30, False)
F_SMALL = font(23, False)
F_PRICE = font(58, True)

def extract_reference_frames():
    if not reference_path or not reference_path.exists():
        return []

    try:
        reader = imageio.get_reader(str(reference_path))
        meta = {}
        try:
            meta = reader.get_meta_data()
        except Exception:
            meta = {}

        fps = meta.get("fps") or 24
        duration = meta.get("duration") or 8
        indexes = [0, int((duration * fps) / 2), max(0, int(duration * fps) - 3)]
        frames = []

        for i, idx in enumerate(indexes, start=1):
            try:
                frame = reader.get_data(idx)
                img = Image.fromarray(frame).convert("RGB")
                img.thumbnail((560, 560))
                frame_path = OUT / f"GP_VIDEO_02_REFERENCE_FRAME_{i}.jpg"
                img.save(frame_path, quality=88)
                frames.append(frame_path)
            except Exception:
                pass

        try:
            reader.close()
        except Exception:
            pass

        return frames
    except Exception:
        return []

reference_frames = extract_reference_frames()

scenes = [
    {
        "title": "Continuacao do Garoto Oxy",
        "duration": 4,
        "line": "Depois do primeiro video, vamos mostrar o Oxy Power em uso real.",
        "screen": "Referencia: publicacao real Hupmix"
    },
    {
        "title": "Prova visual",
        "duration": 5,
        "line": "Mostre o antes: sujeira, gordura, piso ou box pedindo limpeza.",
        "screen": "Antes real, sem exagero"
    },
    {
        "title": "Modo de uso",
        "duration": 6,
        "line": "Aplicar, deixar agir e limpar. Pratico, sem cloro e sem toxicidade.",
        "screen": "Oxigenio Ativo em acao"
    },
    {
        "title": "Resultado",
        "duration": 5,
        "line": "Mostre o depois com comparativo claro e honesto.",
        "screen": "Antes e depois"
    },
    {
        "title": "Oferta e CTA",
        "duration": 5,
        "line": "Oxy Power 5L por R$ 49,90. Passe na HupMix ou chame no WhatsApp.",
        "screen": "R$ 49,90 | WhatsApp"
    },
]

job = {
    "status": "KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY_JOB_READY",
    "created_at": datetime.now().isoformat(),
    "video_id": "GP_VIDEO_02",
    "based_on": {
        "campaign": "Garoto Oxy Power / Oxy Power",
        "instagram_reference": rel(reference_path) if reference_path else None,
        "audit_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
        "caption_score": gp_score
    },
    "mode": "free_local_continuity_render",
    "objective": "Produzir proximo video coerente com a campanha ja publicada, usando a publicacao real como referencia.",
    "scenes": scenes,
    "outputs": {
        "mp4": rel(MP4),
        "storyboard": rel(STORYBOARD),
        "reference_frames": [rel(p) for p in reference_frames]
    },
    "policy": {
        "no_publish": True,
        "no_paid_ai": True,
        "no_scraping": True,
        "no_logged_browser_automation": True,
        "human_gate_required": True
    }
}

JOB.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

def wrap(draw, text, fnt, max_width):
    words = str(text).split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        box = draw.textbbox((0, 0), test, font=fnt)
        if box[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def draw_center(draw, text, y, fnt, fill, max_width, spacing=8):
    for line in wrap(draw, text, fnt, max_width):
        box = draw.textbbox((0, 0), line, font=fnt)
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (box[3] - box[1]) + spacing
    return y

def rounded(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def paste_ref(img, scene_index):
    if not reference_frames:
        return

    ref = reference_frames[scene_index % len(reference_frames)]
    try:
        ref_img = Image.open(ref).convert("RGB")
        ref_img.thumbnail((520, 390))
        x = (WIDTH - ref_img.width) // 2
        y = 235
        img.paste(ref_img, (x, y))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((x-8, y-8, x+ref_img.width+8, y+ref_img.height+8), radius=24, outline=(22,108,74), width=5)
    except Exception:
        pass

def make_frame(scene, scene_index, t, total_t):
    img = Image.new("RGB", (WIDTH, HEIGHT), (246, 248, 247))
    draw = ImageDraw.Draw(img)

    progress = min(max(t / max(total_t, 1), 0), 1)

    draw.rectangle((0, 0, WIDTH, 185), fill=(22, 108, 74))
    draw.rectangle((0, HEIGHT - 155, WIDTH, HEIGHT), fill=(22, 108, 74))
    draw.text((42, 40), "HupMix", font=F_H1, fill=(255, 255, 255))
    draw.text((42, 108), "GP_VIDEO_02 | Continuidade Garoto Oxy", font=F_SMALL, fill=(226, 245, 235))

    draw.rectangle((42, 158, WIDTH-42, 170), fill=(165, 204, 186))
    draw.rectangle((42, 158, int(42 + (WIDTH-84)*progress), 170), fill=(255, 255, 255))

    rounded(draw, (58, 215, WIDTH-58, 650), 34, fill=(255, 255, 255), outline=(216, 230, 222), width=3)
    paste_ref(img, scene_index)

    if not reference_frames:
        draw_center(draw, "Referencia Instagram Hupmix", 350, F_H2, (22,108,74), WIDTH-120)

    y = 700
    y = draw_center(draw, scene["title"], y, F_H1, (20, 60, 45), WIDTH-100)
    y += 18
    y = draw_center(draw, scene["line"], y, F_BODY, (36, 48, 52), WIDTH-110)

    rounded(draw, (70, 990, WIDTH-70, 1075), 24, fill=(232, 241, 236), outline=(204, 222, 212), width=2)
    draw_center(draw, scene["screen"], 1015, F_SMALL, (20, 90, 65), WIDTH-130)

    if scene_index == len(scenes) - 1:
        rounded(draw, (130, 885, WIDTH-130, 960), 26, fill=(255, 241, 190), outline=(225, 190, 90), width=3)
        draw_center(draw, "R$ 49,90", 895, F_PRICE, (88, 66, 10), WIDTH-220)

    draw.text((42, HEIGHT-112), "Proximo video | Coerente com campanha publicada", font=F_SMALL, fill=(255,255,255))
    draw.text((42, HEIGHT-74), "Preview local | Sem publicacao | Sem IA paga", font=F_SMALL, fill=(226,245,235))

    pulse = int(16 * math.sin(progress * math.pi))
    draw.ellipse((WIDTH-102-pulse, 52-pulse, WIDTH-56+pulse, 98+pulse), outline=(255,255,255), width=4)

    return img

tiles = []

writer = imageio.get_writer(str(MP4), fps=FPS, macro_block_size=16)
try:
    for i, scene in enumerate(scenes):
        total_frames = scene["duration"] * FPS
        for f in range(total_frames):
            writer.append_data(np.array(make_frame(scene, i, f, total_frames)))
        tiles.append(make_frame(scene, i, total_frames-1, total_frames).resize((216, 384)))
finally:
    writer.close()

story = Image.new("RGB", (216 * len(tiles), 384), (255,255,255))
for i, tile in enumerate(tiles):
    story.paste(tile, (i*216, 0))
story.save(STORYBOARD)

report = {
    "status": "KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY_READY",
    "created_at": datetime.now().isoformat(),
    "job": rel(JOB),
    "outputs": {
        "mp4": rel(MP4),
        "mp4_size": MP4.stat().st_size,
        "storyboard": rel(STORYBOARD),
        "storyboard_size": STORYBOARD.stat().st_size,
        "reference_frames": [rel(p) for p in reference_frames]
    },
    "policy": job["policy"],
    "next_step": "Abrir painel de producao Hupmix e validar direcao criativa."
}

(REPORTS / "KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

(REPORTS / "KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY.md").write_text(
    "# K-OS Hupmix GP_VIDEO_02 Continuity Factory\n\n"
    "Status: proximo preview local criado com base na campanha real Garoto Oxy.\n\n"
    f"- MP4: {report['outputs']['mp4']} | {report['outputs']['mp4_size']} bytes\n"
    f"- Storyboard: {report['outputs']['storyboard']} | {report['outputs']['storyboard_size']} bytes\n"
    f"- Referencia Instagram: {job['based_on']['instagram_reference']}\n"
    "- Publicacao: bloqueada\n"
    "- IA paga: nao usada\n"
    "- Scraping: nao usado\n",
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False, indent=2))
