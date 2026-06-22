from pathlib import Path
import ast
import json
from datetime import datetime

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")
REPORT_JSON = ROOT / "reports" / "KOS_CODEBASE_STATIC_MAP.json"
REPORT_MD = ROOT / "reports" / "KOS_CODEBASE_STATIC_MAP.md"

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".streamlit",
    "node_modules", ".mypy_cache", ".pytest_cache",
    "local_runtime", "local_secrets", "secrets", "credentials"
}

RISK_KEYWORDS = [
    "subprocess",
    "os.system",
    "webbrowser",
    "requests.",
    "urllib",
    "selenium",
    "playwright",
    "openai",
    "google.generativeai",
    "anthropic",
    "META_ACCESS_TOKEN",
    "ACCESS_TOKEN",
    "publish",
    "upload",
    "delete",
    "Remove-Item"
]

STREAMLIT_KEYWORDS = [
    "st.button",
    "st.form_submit_button",
    "st.text_area",
    "st.chat_input",
    "st.video",
    "st.components",
    "components.html"
]

def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & IGNORE_DIRS)

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def analyze_python(path: Path):
    text = safe_read(path)
    item = {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "lines": text.count("\n") + 1 if text else 0,
        "functions": [],
        "classes": [],
        "imports": [],
        "risk_hits": [],
        "streamlit_hits": []
    }

    for kw in RISK_KEYWORDS:
        if kw in text:
            item["risk_hits"].append(kw)

    for kw in STREAMLIT_KEYWORDS:
        if kw in text:
            item["streamlit_hits"].append(kw)

    try:
        tree = ast.parse(text)
    except Exception as e:
        item["parse_error"] = str(e)
        return item

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            item["functions"].append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            item["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            item["classes"].append(node.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                item["imports"].append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                item["imports"].append(node.module)

    item["functions"] = sorted(set(item["functions"]))
    item["classes"] = sorted(set(item["classes"]))
    item["imports"] = sorted(set(item["imports"]))
    return item

def main():
    py_files = []
    for p in ROOT.rglob("*.py"):
        if not should_skip(p):
            py_files.append(p)

    analyzed = [analyze_python(p) for p in sorted(py_files)]

    high_interest = []
    for item in analyzed:
        score = 0
        if item["risk_hits"]:
            score += 2
        if item["streamlit_hits"]:
            score += 2
        if "pages/" in item["path"]:
            score += 1
        if "scripts/" in item["path"]:
            score += 1
        if "operator" in item["path"].lower():
            score += 2
        if "safe_action" in item["path"].lower():
            score += 2
        if "router" in item["path"].lower():
            score += 2
        if score > 0:
            high_interest.append({**item, "interest_score": score})

    summary = {
        "status": "KOS_CODEBASE_STATIC_MAP_READY",
        "created_at": datetime.now().isoformat(),
        "repo": str(ROOT),
        "policy": {
            "no_external_tool_used": True,
            "no_ai_used": True,
            "no_api_key_used": True,
            "no_install_executed": True,
            "no_publish": True,
            "no_deploy": True
        },
        "totals": {
            "python_files": len(analyzed),
            "files_with_risk_hits": sum(1 for x in analyzed if x["risk_hits"]),
            "files_with_streamlit_hits": sum(1 for x in analyzed if x["streamlit_hits"]),
            "functions_total": sum(len(x["functions"]) for x in analyzed),
            "classes_total": sum(len(x["classes"]) for x in analyzed)
        },
        "top_interest_files": sorted(high_interest, key=lambda x: x["interest_score"], reverse=True)[:80],
        "all_python_files": analyzed
    }

    REPORT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# K-OS Codebase Static Map")
    md.append("")
    md.append("Status: mapa estático criado sem IA, sem instalação externa e sem API.")
    md.append("")
    md.append("## Totais")
    for k, v in summary["totals"].items():
        md.append(f"- {k}: {v}")

    md.append("")
    md.append("## Arquivos de maior interesse")
    for item in summary["top_interest_files"][:40]:
        md.append(f"### {item['path']}")
        md.append(f"- score: {item['interest_score']}")
        md.append(f"- linhas: {item['lines']}")
        md.append(f"- funções: {', '.join(item['functions'][:30]) if item['functions'] else '-'}")
        md.append(f"- classes: {', '.join(item['classes'][:20]) if item['classes'] else '-'}")
        md.append(f"- riscos: {', '.join(item['risk_hits']) if item['risk_hits'] else '-'}")
        md.append(f"- streamlit: {', '.join(item['streamlit_hits']) if item['streamlit_hits'] else '-'}")
        md.append("")

    md.append("## Decisão")
    md.append("Codebase Memory MCP permanece pausado. Este scanner interno entrega o primeiro mapa técnico sem risco operacional.")

    REPORT_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "status": summary["status"],
        "python_files": summary["totals"]["python_files"],
        "files_with_risk_hits": summary["totals"]["files_with_risk_hits"],
        "files_with_streamlit_hits": summary["totals"]["files_with_streamlit_hits"],
        "functions_total": summary["totals"]["functions_total"],
        "classes_total": summary["totals"]["classes_total"],
        "json_report": str(REPORT_JSON.relative_to(ROOT)),
        "md_report": str(REPORT_MD.relative_to(ROOT))
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
