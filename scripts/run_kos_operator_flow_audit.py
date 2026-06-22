from pathlib import Path
import ast
import json
import re
from datetime import datetime

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")

TARGET_PATTERNS = [
    "operator",
    "safe_action",
    "action_router",
    "router",
    "executor",
    "decision",
    "human_decision",
]

RISK_TERMS = [
    "subprocess",
    "os.system",
    "webbrowser",
    "requests.",
    "urllib",
    "openai",
    "google.generativeai",
    "anthropic",
    "publish",
    "upload",
    "delete",
    "ACCESS_TOKEN",
    "META_ACCESS_TOKEN",
]

UI_TERMS = [
    "st.button",
    "st.form_submit_button",
    "st.text_area",
    "st.chat_input",
    "st.video",
    "components.html",
    "st.session_state",
]

IGNORE_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "local_runtime",
    "local_secrets",
    "secrets",
    "credentials",
    "_local_quarantine",
    ".codex_phase5",
    ".tmp",
}

IGNORE_PATH_FRAGMENTS = [
    "/_local_quarantine/",
    "\\_local_quarantine\\",
    "/node_modules/",
    "\\node_modules\\",
    "/.git/",
    "\\.git\\",
    "/local_runtime/",
    "\\local_runtime\\",
    "/local_secrets/",
    "\\local_secrets\\",
]

def rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_DIR_NAMES:
        return True
    raw = str(path)
    for frag in IGNORE_PATH_FRAGMENTS:
        if frag in raw:
            return True
    return False

def safe_read(path: Path) -> str:
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, PermissionError, OSError, UnicodeError):
        return ""

def interesting_file(path: Path, text: str) -> bool:
    rel = rel_path(path).lower()
    if any(p in rel for p in TARGET_PATTERNS):
        return True
    if any(term in text for term in UI_TERMS):
        return True
    if any(term in text for term in RISK_TERMS):
        return True
    return False

def analyze(path: Path):
    text = safe_read(path)
    rel = rel_path(path)

    item = {
        "path": rel,
        "lines": text.count("\n") + 1 if text else 0,
        "functions": [],
        "classes": [],
        "imports": [],
        "called_names": [],
        "subprocess_lines": [],
        "ui_lines": [],
        "risk_hits": [],
        "route_like_strings": [],
        "writes_runtime_or_reports": [],
    }

    if not text:
        item["read_error_or_empty"] = True
        return item

    for term in RISK_TERMS:
        if term in text:
            item["risk_hits"].append(term)

    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if any(term in stripped for term in ["subprocess", "os.system", "webbrowser"]):
            item["subprocess_lines"].append({"line": idx, "text": stripped[:300]})

        if any(term in stripped for term in UI_TERMS):
            item["ui_lines"].append({"line": idx, "text": stripped[:300]})

        if any(x in stripped for x in ["local_runtime", "reports", "decision_queue", "safe_action", "action_router"]):
            item["writes_runtime_or_reports"].append({"line": idx, "text": stripped[:300]})

        if re.search(r"route|intent|action_type|builder|build_", stripped, re.I):
            if len(item["route_like_strings"]) < 80:
                item["route_like_strings"].append({"line": idx, "text": stripped[:300]})

    try:
        tree = ast.parse(text)
    except Exception as e:
        item["parse_error"] = str(e)
        return item

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            item["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            item["classes"].append(node.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                item["imports"].append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                item["imports"].append(node.module)
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name:
                item["called_names"].append(name)

    for key in ["functions", "classes", "imports", "called_names", "risk_hits"]:
        item[key] = sorted(set(item[key]))

    return item

def main():
    candidates = []
    for path in ROOT.rglob("*.py"):
        if should_skip(path):
            continue
        candidates.append(path)

    analyzed = []
    skipped_empty = 0

    for path in sorted(candidates):
        text = safe_read(path)
        if not text:
            skipped_empty += 1
            continue
        if interesting_file(path, text):
            analyzed.append(analyze(path))

    core = []
    for item in analyzed:
        low = item["path"].lower()
        score = 0
        if "pages/kos_operator_chat.py" in low:
            score += 10
        if "operator" in low:
            score += 5
        if "safe_action" in low:
            score += 5
        if "router" in low:
            score += 5
        if "executor" in low:
            score += 4
        if item["subprocess_lines"]:
            score += 3
        if item["ui_lines"]:
            score += 2
        if item["risk_hits"]:
            score += 2
        if score > 0:
            core.append({**item, "score": score})

    core = sorted(core, key=lambda x: (x["score"], x["lines"]), reverse=True)

    report = {
        "status": "KOS_OPERATOR_FLOW_AUDIT_READY",
        "created_at": datetime.now().isoformat(),
        "repo": str(ROOT),
        "policy": {
            "no_ai_used": True,
            "no_external_tool_used": True,
            "no_api_key_used": True,
            "no_install_executed": True,
            "no_publish": True,
            "no_deploy": True
        },
        "summary": {
            "candidate_python_files": len(candidates),
            "interesting_python_files": len(analyzed),
            "core_files": len(core),
            "skipped_empty_or_unreadable": skipped_empty,
            "files_with_subprocess_or_browser": sum(1 for x in analyzed if x["subprocess_lines"]),
            "files_with_ui_lines": sum(1 for x in analyzed if x["ui_lines"]),
            "files_with_runtime_or_reports": sum(1 for x in analyzed if x["writes_runtime_or_reports"]),
        },
        "core_flow_files": core[:80],
        "recommendation": {
            "next_step": "criar painel de diagnostico compacto do fluxo dentro do Operator Chat",
            "priority": "Operator Chat primeiro, depois Router, depois Safe Action Executor",
            "do_not_do_yet": [
                "nao instalar Codebase Memory MCP",
                "nao conectar IA paga",
                "nao conectar gerador de video",
                "nao mexer em publicacao"
            ]
        }
    }

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)

    json_path = reports / "KOS_OPERATOR_FLOW_AUDIT.json"
    md_path = reports / "KOS_OPERATOR_FLOW_AUDIT.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# K-OS Operator Flow Audit")
    md.append("")
    md.append("Status: auditoria do fluxo operador criada sem IA e sem ferramentas externas.")
    md.append("")
    md.append("## Resumo")
    for k, v in report["summary"].items():
        md.append(f"- {k}: {v}")

    md.append("")
    md.append("## Arquivos centrais")
    for item in core[:30]:
        md.append(f"### {item['path']}")
        md.append(f"- score: {item['score']}")
        md.append(f"- linhas: {item['lines']}")
        md.append(f"- funcoes: {', '.join(item['functions'][:25]) if item['functions'] else '-'}")
        md.append(f"- riscos: {', '.join(item['risk_hits']) if item['risk_hits'] else '-'}")
        md.append(f"- ui_hits: {len(item['ui_lines'])}")
        md.append(f"- subprocess/browser hits: {len(item['subprocess_lines'])}")
        md.append(f"- runtime/report hits: {len(item['writes_runtime_or_reports'])}")
        md.append("")

    md.append("## Decisao")
    md.append("Proximo passo recomendado: criar painel de diagnostico do fluxo no Operator Chat.")
    md.append("Ainda nao instalar Codebase Memory MCP, IA paga ou geradores de video.")

    md_path.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "summary": report["summary"],
        "top_core_files": [
            {
                "path": x["path"],
                "score": x["score"],
                "lines": x["lines"],
                "risk_hits": x["risk_hits"][:10],
                "ui_hits": len(x["ui_lines"]),
                "subprocess_hits": len(x["subprocess_lines"])
            }
            for x in core[:10]
        ],
        "json_report": "reports/KOS_OPERATOR_FLOW_AUDIT.json",
        "md_report": "reports/KOS_OPERATOR_FLOW_AUDIT.md"
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
