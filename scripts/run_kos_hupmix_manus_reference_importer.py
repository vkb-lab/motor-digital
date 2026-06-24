
from pathlib import Path
from datetime import datetime
import json
import zipfile
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "content_packs" / "_incoming_packages"
RUNTIME = ROOT / "local_runtime" / "kos_reference_imports" / "hupmix_manus"
KNOWLEDGE = ROOT / "memory" / "kos_knowledge"
SKILLS = ROOT / "memory" / "kos_skills"
REPORTS = ROOT / "reports"

for p in [INBOX, RUNTIME, KNOWLEDGE, SKILLS, REPORTS]:
    p.mkdir(parents=True, exist_ok=True)

def rel(path):
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def slug(value):
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower() or "package"

def write_json(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2)
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return
    path.write_text(content, encoding="utf-8")

def write_text(path, content):
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return
    path.write_text(content, encoding="utf-8")

def latest_zip():
    zips = list(INBOX.glob("*.zip"))
    if not zips:
        return None
    zips.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return zips[0]

def safe_extract(zip_path, target):
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            name = member.filename.replace("\\", "/")
            if name.startswith("/") or ".." in Path(name).parts:
                continue
            z.extract(member, target)

def classify(path):
    name = path.name.lower()
    ext = path.suffix.lower()

    if ext in [".png", ".jpg", ".jpeg", ".webp"]:
        kind = "image"
    elif ext in [".mp4", ".mov", ".m4v", ".avi", ".webm"]:
        kind = "video"
    elif ext in [".md", ".txt", ".html", ".htm", ".json", ".csv"]:
        kind = "document"
    else:
        kind = "other"

    tags = []
    rules = {
        "skill": ["skill"],
        "prompt": ["prompt"],
        "storytelling": ["story", "narrative", "roteiro", "conteudo", "plano"],
        "automation": ["telegram", "manychat", "whatsapp", "bot", "automacao", "dns"],
        "instagram": ["instagram", "insta", "post"],
        "product": ["oxy", "oxypower", "produto", "product"],
        "character": ["garoto", "personagem", "concept", "nobg"],
        "site": ["html", "site", "preview", "index"],
    }

    for tag, words in rules.items():
        if any(w in name for w in words):
            tags.append(tag)

    return kind, sorted(set(tags))

def excerpt(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:900].strip()
    except Exception:
        return ""

def main():
    zip_path = latest_zip()

    if not zip_path:
        event = {
            "status": "KOS_HUPMIX_MANUS_REFERENCE_IMPORTER_WAITING_FOR_ZIP",
            "created_at": datetime.now().isoformat(),
            "inbox": rel(INBOX),
            "next_step": "Colocar ZIP Manus/Hupmix em content_packs/_incoming_packages."
        }
        write_json(RUNTIME / "status.json", event)
        print(json.dumps(event, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    zip_hash = sha256(zip_path)
    extract_dir = RUNTIME / f"{slug(zip_path.stem)}_{zip_hash[:12]}"

    if not extract_dir.exists():
        safe_extract(zip_path, extract_dir)

    counts = {
        "document": 0,
        "image": 0,
        "video": 0,
        "other": 0,
        "skill": 0,
        "prompt": 0,
        "automation": 0,
        "storytelling": 0,
        "instagram": 0,
        "product": 0,
        "character": 0
    }

    files = []

    for path in sorted([p for p in extract_dir.rglob("*") if p.is_file()]):
        kind, tags = classify(path)
        counts[kind] = counts.get(kind, 0) + 1
        for tag in tags:
            counts[tag] = counts.get(tag, 0) + 1

        item = {
            "name": path.name,
            "runtime_path": rel(path),
            "type": kind,
            "tags": tags,
            "size_bytes": path.stat().st_size
        }

        if kind == "document":
            item["excerpt"] = excerpt(path)

        files.append(item)

    index = {
        "status": "KOS_HUPMIX_MANUS_REFERENCE_INDEX_READY",
        "created_at": datetime.now().isoformat(),
        "source_zip": rel(zip_path),
        "zip_sha256": zip_hash,
        "extract_dir": rel(extract_dir),
        "counts": counts,
        "files": files,
        "principle": "Hupmix e caso-escola. O pacote Manus vira referencia criativa reutilizavel para outras verticais."
    }

    write_json(KNOWLEDGE / "KOS_HUPMIX_MANUS_REFERENCE_INDEX.json", index)

    md = ["# KOS Hupmix Manus Reference Index", "", "Status: READY", "", "## Counts"]
    for k, v in counts.items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Arquivos")
    for item in files[:120]:
        md.append(f"- `{item['runtime_path']}` | {item['type']} | {', '.join(item['tags'])}")
    write_text(KNOWLEDGE / "KOS_HUPMIX_MANUS_REFERENCE_INDEX.md", "\n".join(md))

    write_text(SKILLS / "KOS_MANUS_COMPATIBLE_CREATIVE_PRODUCTION_SKILL_V1.md", """# KOS Manus-Compatible Creative Production Skill V1

Status: READY

## Funcao
Transformar pacotes criativos externos em referencia operacional reutilizavel.

## Pipeline
1. Importar pacote
2. Classificar docs, imagens, videos, prompts e automacoes
3. Extrair padroes narrativos
4. Criar skill do cliente/personagem
5. Criar briefing para editor
6. Criar prompts para IA visual quando autorizada
7. Gerar preview local
8. Comparar com referencia
9. Pedir OK humano
10. Promover aprendizado universal

## Regra
Hupmix e caso-escola. O processo deve servir para loja, SaaS, agencia, clinica e operacoes maiores.
""")

    write_text(SKILLS / "KOS_GP_CREATOR_SKILL_V3_MANUS_COMPATIBLE.md", """# KOS GP Creator Skill V3 — Manus Compatible

Status: READY

## Funcao
Elevar o Garoto Oxy Power de preview tecnico para linha criativa compativel com referencia Manus.

## Estrutura de video
1. Hook visual forte
2. Personagem consistente
3. Produto em destaque
4. Problema real
5. Demonstracao ou prova
6. Beneficio simples
7. Oferta
8. CTA

## Regra de verdade visual
Se nao existe footage real, gerar conceito, storyboard, prompt ou briefing.
Nao apresentar cena inventada como prova real.
""")

    upgrade = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_PLAN_READY",
        "created_at": datetime.now().isoformat(),
        "current_state": "GP_VIDEO_02 tem preview tecnico gerado com asset real do Instagram.",
        "target_state": "Criar versao Manus-compatible com roteiro, score, briefing, prompts e plano de edicao.",
        "inputs": counts,
        "next_modules": [
            "KOS_HUPMIX_CREATIVE_REFERENCE_SCORER_V1",
            "KOS_GP_VIDEO_EDITOR_BRIEF_GENERATOR_V1",
            "KOS_GP_VIDEO_PROMPT_PACK_GENERATOR_V1",
            "KOS_GP_VIDEO_02_MANUS_STYLE_PREVIEW_V1"
        ],
        "policy": {
            "no_publish": True,
            "no_paid_ai_without_approval": True,
            "no_fake_proof": True,
            "human_gate_required": True
        }
    }

    write_json(KNOWLEDGE / "KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_PLAN.json", upgrade)

    report = {
        "status": "KOS_HUPMIX_MANUS_REFERENCE_IMPORTER_V1_READY",
        "created_at": datetime.now().isoformat(),
        "source_zip": rel(zip_path),
        "extract_dir": rel(extract_dir),
        "index": "memory/kos_knowledge/KOS_HUPMIX_MANUS_REFERENCE_INDEX.json",
        "creative_skill": "memory/kos_skills/KOS_MANUS_COMPATIBLE_CREATIVE_PRODUCTION_SKILL_V1.md",
        "gp_skill": "memory/kos_skills/KOS_GP_CREATOR_SKILL_V3_MANUS_COMPATIBLE.md",
        "upgrade_plan": "memory/kos_knowledge/KOS_HUPMIX_GP_VIDEO_02_MANUS_UPGRADE_PLAN.json",
        "counts": counts,
        "next_step": "Melhorar GP_VIDEO_02 usando score, briefing e prompts Manus-compatible."
    }

    write_json(REPORTS / "KOS_HUPMIX_MANUS_REFERENCE_IMPORTER_V1.json", report)
    write_text(REPORTS / "KOS_HUPMIX_MANUS_REFERENCE_IMPORTER_V1.md", "# KOS Hupmix Manus Reference Importer V1\n\nStatus: READY\n\nPacote Manus/Hupmix importado como referencia criativa reutilizavel.\n")
    write_json(RUNTIME / "status.json", report)

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
