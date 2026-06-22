from pathlib import Path
from datetime import datetime
import json
import subprocess
import re

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")
REPORTS = ROOT / "reports"
GOV = ROOT / "memory" / "kos_governance"
SCRIPTS = ROOT / "scripts"

REPORTS.mkdir(parents=True, exist_ok=True)
GOV.mkdir(parents=True, exist_ok=True)
SCRIPTS.mkdir(parents=True, exist_ok=True)

NOW = datetime.now().isoformat()

SENSITIVE_PARTS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    "local_secrets", "secrets", "credentials", "private"
}

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def safe_exists(path: str) -> bool:
    return (ROOT / path).exists()

def read_text(path: Path) -> str:
    try:
        if any(part.lower() in SENSITIVE_PARTS for part in path.parts):
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def read_json(path: str):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception:
        return None

def json_status(path: str) -> str:
    data = read_json(path)
    if isinstance(data, dict):
        return str(data.get("status") or "UNKNOWN")
    return "MISSING"

def git(args):
    try:
        p = subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True, text=True, timeout=30)
        return p.stdout.strip().splitlines()
    except Exception:
        return []

def allowed_file(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return not bool(parts & SENSITIVE_PARTS)

def collect_files(pattern: str):
    return [p for p in ROOT.rglob(pattern) if allowed_file(p)]

python_files = collect_files("*.py")
json_files = collect_files("*.json")
md_files = collect_files("*.md")
cmd_files = collect_files("*.cmd")

folders = {
    "agents": ROOT / "agents",
    "pages": ROOT / "pages",
    "scripts": ROOT / "scripts",
    "memory": ROOT / "memory",
    "reports": ROOT / "reports",
    "campaigns": ROOT / "campaigns",
    "content_packs": ROOT / "content_packs",
    "live": ROOT / "live",
    "local_runtime": ROOT / "local_runtime",
}

folder_status = {}
for name, path in folders.items():
    folder_status[name] = {
        "exists": path.exists(),
        "py_files": len(list(path.rglob("*.py"))) if path.exists() and name not in ["local_runtime", "live"] else 0,
        "json_files": len(list(path.rglob("*.json"))) if path.exists() and name not in ["local_runtime", "live"] else 0
    }

signals = {
    "operator_chat": [],
    "agents": [],
    "routers": [],
    "safe_actions": [],
    "auditors": [],
    "video_factories": [],
    "research": [],
    "file_intake": [],
    "meta_instagram": [],
    "governance": [],
    "campaigns": [],
    "memory": [],
}

for path in python_files:
    r = rel(path)
    name = path.name.lower()
    text = read_text(path).lower()

    if "streamlit" in text or "st." in text:
        signals["operator_chat"].append(r)

    if "/agents/" in r.lower() or "\\agents\\" in str(path).lower() or "agent" in name:
        signals["agents"].append(r)

    if "router" in name or "route" in text:
        signals["routers"].append(r)

    if "safe_action" in name or "safe action" in text or "human_gate" in text or "human gate" in text:
        signals["safe_actions"].append(r)

    if "audit" in name or "auditor" in text:
        signals["auditors"].append(r)

    if "video" in name or "factory" in name or ".mp4" in text or "imageio" in text:
        signals["video_factories"].append(r)

    if "research" in name or "public_sources_only" in text or "no_scraping" in text:
        signals["research"].append(r)

    if "file_uploader" in text or "assets_inbox" in text or "intake" in name:
        signals["file_intake"].append(r)

    if "graph.facebook.com" in text or "meta graph" in text or "instagram" in text:
        signals["meta_instagram"].append(r)

    if "no_publish" in text or "human_gate_required" in text or "governance" in r.lower():
        signals["governance"].append(r)

for path in json_files + md_files:
    r = rel(path)
    low = r.lower()
    if low.startswith("campaigns/"):
        signals["campaigns"].append(r)
    if low.startswith("memory/"):
        signals["memory"].append(r)
    if "governance" in low or "policy" in low:
        signals["governance"].append(r)

for key in signals:
    signals[key] = sorted(list(set(signals[key])))[:120]

known_capabilities = [
    {
        "id": "operator_chat",
        "name": "K-OS Operator Chat",
        "type": "cockpit",
        "status": "ACTIVE" if safe_exists("pages/KOS_Operator_Chat.py") else "MISSING",
        "path": "pages/KOS_Operator_Chat.py",
        "autonomy_level": 2,
        "works_now": safe_exists("pages/KOS_Operator_Chat.py"),
        "can_act_alone": False,
        "requires_human_gate": True,
        "what_it_does": "Entrada principal. Recebe pedido unico, escolhe rota e mantem acoes reais gateadas."
    },
    {
        "id": "hupmix_instagram_readonly",
        "name": "Hupmix Instagram Meta Graph Read-only",
        "type": "integration",
        "status": json_status("reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"),
        "path": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
        "autonomy_level": 3,
        "works_now": safe_exists("reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"),
        "can_act_alone": True,
        "requires_human_gate": False,
        "what_it_does": "Consulta Instagram Hupmix via Meta Graph oficial em modo leitura e baixa midia permitida."
    },
    {
        "id": "hupmix_gp_video_01_review",
        "name": "Hupmix GP_VIDEO_01 Review",
        "type": "campaign_video",
        "status": "READY" if safe_exists("local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4") else "MISSING",
        "path": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4",
        "autonomy_level": 2,
        "works_now": safe_exists("local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4"),
        "can_act_alone": False,
        "requires_human_gate": True,
        "what_it_does": "Mostra video local, storyboard e permite decisao humana."
    },
    {
        "id": "hupmix_gp_video_02_real_assets",
        "name": "Hupmix GP_VIDEO_02 Real Asset Production",
        "type": "campaign_video",
        "status": json_status("reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json"),
        "path": "scripts/run_kos_hupmix_gp_video_02_real_asset_audit.py",
        "autonomy_level": 2,
        "works_now": safe_exists("scripts/run_kos_hupmix_gp_video_02_real_asset_audit.py"),
        "can_act_alone": False,
        "requires_human_gate": True,
        "what_it_does": "Nao gera video fake. Espera assets reais, audita e cria preview real local."
    },
    {
        "id": "file_intake",
        "name": "K-OS File Intake",
        "type": "input",
        "status": "ACTIVE" if safe_exists("content_packs") else "MISSING",
        "path": "content_packs/",
        "autonomy_level": 2,
        "works_now": safe_exists("content_packs"),
        "can_act_alone": True,
        "requires_human_gate": False,
        "what_it_does": "Recebe anexos e direciona arquivos para assets_inbox."
    },
    {
        "id": "research_continuity",
        "name": "Research & Continuity Center",
        "type": "research",
        "status": "ACTIVE" if safe_exists("memory/kos_governance/KOS_RESEARCH_AUTONOMY_POLICY.json") else "PARTIAL",
        "path": "memory/kos_governance/",
        "autonomy_level": 1,
        "works_now": safe_exists("memory/kos_governance"),
        "can_act_alone": True,
        "requires_human_gate": False,
        "what_it_does": "Registra pesquisa publica e verifica continuidade antes de criar algo novo."
    },
    {
        "id": "safe_action_governance",
        "name": "Safe Action / Human Gate",
        "type": "governance",
        "status": "ACTIVE" if signals["safe_actions"] else "PARTIAL",
        "path": "local_runtime/kos_safe_actions / live/human_decision_center",
        "autonomy_level": 2,
        "works_now": bool(signals["safe_actions"]),
        "can_act_alone": False,
        "requires_human_gate": True,
        "what_it_does": "Mantem execucoes reais bloqueadas ate aprovacao humana."
    },
    {
        "id": "operator_flow_audit",
        "name": "Operator Flow Audit",
        "type": "audit",
        "status": json_status("reports/KOS_OPERATOR_FLOW_AUDIT.json"),
        "path": "reports/KOS_OPERATOR_FLOW_AUDIT.json",
        "autonomy_level": 1,
        "works_now": safe_exists("reports/KOS_OPERATOR_FLOW_AUDIT.json"),
        "can_act_alone": True,
        "requires_human_gate": False,
        "what_it_does": "Audita fluxo do Operator Chat, riscos e pontos de rota."
    },
    {
        "id": "codebase_static_map",
        "name": "Codebase Static Map",
        "type": "audit",
        "status": json_status("reports/KOS_CODEBASE_STATIC_MAP.json"),
        "path": "reports/KOS_CODEBASE_STATIC_MAP.json",
        "autonomy_level": 1,
        "works_now": safe_exists("reports/KOS_CODEBASE_STATIC_MAP.json"),
        "can_act_alone": True,
        "requires_human_gate": False,
        "what_it_does": "Mapeia codigo, funcoes, classes e riscos."
    }
]

autonomy_levels = {
    "0": {"name": "Manual", "description": "Operador faz tudo. K-OS apenas mostra informacao."},
    "1": {"name": "Auditoria read-only", "description": "K-OS le arquivos, interpreta, gera relatorios e nao altera sistemas externos."},
    "2": {"name": "Execucao local gateada", "description": "K-OS cria arquivos, briefings, previews e registros locais. Acoes reais exigem OK humano."},
    "3": {"name": "Integracao externa read-only", "description": "K-OS usa APIs oficiais em leitura, sem publicar, comentar, deletar ou enviar."},
    "4": {"name": "Acao externa gateada", "description": "K-OS prepara acao externa, mas so executa com gate humano separado."},
    "5": {"name": "Autonomia plena", "description": "Bloqueado. Publicacao, deploy e gasto automatico nao autorizados."}
}

policy = {
    "current_max_autonomy_level": 3,
    "external_publish_enabled": False,
    "external_send_enabled": False,
    "paid_ai_enabled": False,
    "scraping_enabled": False,
    "logged_browser_automation_enabled": False,
    "manual_approval_required_for_real_actions": True,
    "default_mode": "read_only_or_local_gated"
}

intelligence_connected = {
    "python_executor": True,
    "streamlit_cockpit": safe_exists("pages/KOS_Operator_Chat.py"),
    "github_memory": True,
    "json_memory": safe_exists("memory"),
    "meta_graph_readonly": safe_exists("local_runtime/kos_secrets/meta_access_token.txt") and safe_exists("reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"),
    "local_video_render": safe_exists("scripts/run_kos_hupmix_gp_video_02_real_asset_audit.py"),
    "file_intake": safe_exists("content_packs"),
    "public_research_registry": safe_exists("local_runtime/kos_research_requests") or safe_exists("memory/kos_governance/KOS_RESEARCH_AUTONOMY_POLICY.json"),
    "paid_ai": False,
    "logged_browser_automation": False
}

gaps = []

op_text = read_text(ROOT / "pages" / "KOS_Operator_Chat.py") if safe_exists("pages/KOS_Operator_Chat.py") else ""
if "Entendi" in op_text:
    gaps.append({
        "id": "stale_default_response",
        "severity": "medium",
        "impact": "polui tela e confunde o operador",
        "fix": "Criar limpador central de estado quando painel especializado abre."
    })

if not safe_exists("memory/kos_governance/KOS_CAPABILITY_REGISTRY.json"):
    gaps.append({
        "id": "capability_registry_missing_before_now",
        "severity": "high",
        "impact": "K-OS nao tinha fonte central para saber o que ja consegue fazer.",
        "fix": "Criar e conectar registry ao roteador."
    })

gp02 = read_json("reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json")
if isinstance(gp02, dict) and gp02.get("status") == "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS":
    gaps.append({
        "id": "gp_video_02_waiting_real_assets",
        "severity": "expected",
        "impact": "Nao existe proximo video real sem assets reais.",
        "fix": "Anexar footage/fotos reais na aba Assets reais."
    })

timeline = git(["--no-pager", "log", "--oneline", "-30"])
git_status = git(["--no-pager", "status", "--short"])

working = [c for c in known_capabilities if c["works_now"]]
blocked = [c for c in known_capabilities if not c["works_now"]]

capability_registry = {
    "status": "KOS_CAPABILITY_REGISTRY_READY",
    "created_at": NOW,
    "policy": policy,
    "autonomy_levels": autonomy_levels,
    "intelligence_connected": intelligence_connected,
    "capabilities": known_capabilities,
    "routing_rules": {
        "check_continuity_before_new_work": True,
        "use_capability_registry_before_router": True,
        "require_real_assets_before_real_video": True,
        "external_publish_blocked": True,
        "paid_ai_blocked": True,
        "scraping_blocked": True
    }
}

audit = {
    "status": "KOS_OPERATIONAL_MASTER_AUDIT_V1_READY",
    "created_at": NOW,
    "repo": str(ROOT),
    "summary": {
        "python_files": len(python_files),
        "json_files": len(json_files),
        "md_files": len(md_files),
        "cmd_files": len(cmd_files),
        "known_capabilities": len(known_capabilities),
        "working_capabilities": len(working),
        "blocked_or_partial_capabilities": len(blocked),
        "current_max_autonomy_level": policy["current_max_autonomy_level"],
        "publish_blocked": True,
        "paid_ai_blocked": True,
        "scraping_blocked": True
    },
    "folder_status": folder_status,
    "what_works_now": working,
    "what_is_blocked_or_partial": blocked,
    "intelligence_connected": intelligence_connected,
    "autonomy_levels": autonomy_levels,
    "policy": policy,
    "capability_signals": signals,
    "gaps": gaps,
    "git": {
        "status": git_status,
        "timeline_recent": timeline
    },
    "line_of_time_position": {
        "phase": "capability_registry_and_autonomy_mapping",
        "meaning": "Saiu da criacao isolada de botoes/modulos e entrou na fase de sistema que sabe suas proprias capacidades.",
        "next_phase": "capability_router_connected_to_operator_chat"
    },
    "next_steps": [
        {
            "priority": 1,
            "action": "Conectar Operator Chat ao KOS_CAPABILITY_REGISTRY antes do roteador generico.",
            "impact": "alto",
            "risk": "baixo"
        },
        {
            "priority": 2,
            "action": "Criar limpeza central de resposta stale/Entendi para paineis especializados.",
            "impact": "medio",
            "risk": "baixo"
        },
        {
            "priority": 3,
            "action": "Criar Capability Executor com input, output, permissao e gate por capacidade.",
            "impact": "muito alto",
            "risk": "medio"
        },
        {
            "priority": 4,
            "action": "Criar Autonomy Dashboard dentro do Operator Chat.",
            "impact": "alto",
            "risk": "baixo"
        }
    ]
}

(REPORTS / "KOS_OPERATIONAL_MASTER_AUDIT_V1.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
(GOV / "KOS_CAPABILITY_REGISTRY.json").write_text(json.dumps(capability_registry, ensure_ascii=False, indent=2), encoding="utf-8")
(GOV / "KOS_AUTONOMY_LEVELS.json").write_text(json.dumps({
    "status": "KOS_AUTONOMY_LEVELS_READY",
    "created_at": NOW,
    "current_max_autonomy_level": policy["current_max_autonomy_level"],
    "levels": autonomy_levels,
    "policy": policy
}, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# K-OS Operational Master Audit V1")
md.append("")
md.append(f"Status: {audit['status']}")
md.append("")
md.append("## Onde estamos")
md.append("")
md.append(audit["line_of_time_position"]["meaning"])
md.append("")
md.append("## Resumo")
for k, v in audit["summary"].items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Inteligencia conectada")
for k, v in intelligence_connected.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## O que funciona agora")
for c in working:
    md.append(f"- {c['name']} | nivel {c['autonomy_level']} | {c['status']} | {c['what_it_does']}")
md.append("")
md.append("## Bloqueado ou parcial")
for c in blocked:
    md.append(f"- {c['name']} | {c['status']} | {c['path']}")
md.append("")
md.append("## Gargalos")
for g in gaps:
    md.append(f"- {g['id']} | {g['severity']} | {g['impact']} | fix: {g['fix']}")
md.append("")
md.append("## Proximos passos")
for s in audit["next_steps"]:
    md.append(f"{s['priority']}. {s['action']} | impacto: {s['impact']} | risco: {s['risk']}")
md.append("")
md.append("## Timeline Git recente")
for line in timeline[:20]:
    md.append(f"- {line}")

(REPORTS / "KOS_OPERATIONAL_MASTER_AUDIT_V1.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps({
    "status": audit["status"],
    "working_capabilities": audit["summary"]["working_capabilities"],
    "known_capabilities": audit["summary"]["known_capabilities"],
    "current_max_autonomy_level": policy["current_max_autonomy_level"],
    "intelligence_connected": intelligence_connected,
    "gaps_count": len(gaps),
    "phase": audit["line_of_time_position"]["phase"],
    "capability_registry": "memory/kos_governance/KOS_CAPABILITY_REGISTRY.json",
    "master_audit": "reports/KOS_OPERATIONAL_MASTER_AUDIT_V1.json",
    "next_step": "Conectar Operator Chat ao Capability Registry."
}, ensure_ascii=False, indent=2))
