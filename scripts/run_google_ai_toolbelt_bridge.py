from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json"
REPORT_DIR = ROOT / "reports" / "google_ai_toolbelt"


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise SystemExit(f"Registry not found: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8-sig"))


def find_tool(registry: dict[str, Any], tool_id: str) -> dict[str, Any]:
    for tool in registry.get("tools", []):
        if tool.get("id") == tool_id:
            return tool
    available = ", ".join(sorted([tool.get("id", "") for tool in registry.get("tools", [])]))
    raise SystemExit(f"Tool not found: {tool_id}. Available: {available}")


def write_report(name: str, content: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{stamp()}_{name}.md"
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def make_tool_briefing(registry: dict[str, Any], tool_id: str, project: str, goal: str) -> str:
    tool = find_tool(registry, tool_id)
    uses = tool.get("kos_use", [])
    expected_inputs = tool.get("expected_inputs", [])
    expected_outputs = tool.get("expected_outputs", [])
    human_gate = tool.get("human_gate", [])

    lines = [
        f"# K-OS Google AI Tool Briefing - {tool.get('name')}",
        "",
        f"Project: {project}",
        f"Goal: {goal}",
        f"Tool ID: {tool.get('id')}",
        f"Provider: {tool.get('provider')}",
        f"URL: {tool.get('url')}",
        f"Connection type: {tool.get('connection_type')}",
        f"API status: {tool.get('api_status')}",
        "",
        "## When K-OS should use this tool",
    ]

    for item in uses:
        lines.append(f"- {item}")

    if expected_inputs:
        lines += ["", "## Inputs to prepare"]
        for item in expected_inputs:
            lines.append(f"- {item}")

    if expected_outputs:
        lines += ["", "## Outputs to collect"]
        for item in expected_outputs:
            lines.append(f"- {item}")

    if human_gate:
        lines += ["", "## Human Gate"]
        for item in human_gate:
            lines.append(f"- {item}")

    lines += [
        "",
        "## Prompt / briefing to paste",
        "",
        "Use this project context:",
        f"- Project: {project}",
        f"- Objective: {goal}",
        "- Build using the Kaizen/K-OS ecosystem.",
        "- Keep the output practical, reusable and ready for handoff.",
        "- Prefer assets that can be saved back into the K-OS Bau.",
        "",
        "Deliver:",
        "1. concrete output;",
        "2. assumptions;",
        "3. next execution step;",
        "4. files or assets to save;",
        "5. risks or manual decisions.",
        "",
        "## K-OS follow-up",
        "",
        "- Save prompt used.",
        "- Save output summary.",
        "- Save screenshots/exports manually when applicable.",
        "- Register final artifact in reports/google_ai_toolbelt or memory/kos_knowledge.",
        "- Do not claim API automation when the tool was browser-assisted.",
    ]

    return "\n".join(lines)


def make_subsidy_pack(registry: dict[str, Any], project: str, goal: str) -> str:
    project_info = registry.get("official_project", {})
    positioning = registry.get("startup_subsidy_positioning", {})

    workflow = [
        ("notebooklm", "Research, source-grounded narrative and pitch evidence."),
        ("google_ai_studio", "Gemini model experiments and AI architecture proof."),
        ("stitch", "UI screens and product interface concept."),
        ("mixboard", "Concept board and visual direction."),
        ("pomelli", "On-brand campaign and go-to-market content."),
        ("flow", "Pitch/demo video concept."),
        ("flow_music_producerai", "Sonic branding or campaign soundtrack concept."),
        ("antigravity", "Agentic development and code execution workflow."),
        ("gmail_operator", "Operational proof: real Workspace/Gmail connection already working."),
    ]

    lines = [
        "# K-OS Google Startup Subsidy Pack",
        "",
        f"Project: {project}",
        f"Goal: {goal}",
        "",
        "## Official Google/K-OS context",
        "",
        f"- Organization: {project_info.get('organization')}",
        f"- Main app: {project_info.get('main_app')}",
        f"- Domain: {project_info.get('domain')}",
        f"- Google Cloud project: {project_info.get('google_cloud_project_id')}",
        f"- OAuth app: {project_info.get('google_oauth_app')}",
        "",
        "## Positioning",
        "",
        positioning.get("message", "K-OS orchestrates Google tools into real execution."),
        "",
        "## Tool workflow",
    ]

    for tool_id, role in workflow:
        if tool_id == "gmail_operator":
            lines.append(f"- Gmail Operator: {role}")
            continue
        try:
            tool = find_tool(registry, tool_id)
            lines.append(f"- {tool.get('name')}: {role}")
        except SystemExit:
            lines.append(f"- {tool_id}: {role}")

    lines += [
        "",
        "## Evidence assets to prepare",
    ]

    for item in positioning.get("proof_assets_to_prepare", []):
        lines.append(f"- {item}")

    lines += [
        "",
        "## Recommended demo story",
        "",
        "1. Founder asks K-OS for a product/campaign/startup asset.",
        "2. K-OS reads Bau and project context.",
        "3. K-OS chooses Google tools based on task type.",
        "4. NotebookLM/Gemini create research and logic.",
        "5. Stitch creates UI concept.",
        "6. Pomelli/Mixboard/Flow create campaign and visuals.",
        "7. Antigravity/GitHub support implementation.",
        "8. Gmail Operator proves Workspace integration.",
        "9. K-OS stores evidence, reports and handoff.",
        "",
        "## Next action",
        "",
        "Create a live demo path for one project: kaizen-home, Casa da Limpeza, Hupmix or Ki-Publica.",
    ]

    return "\n".join(lines)


def run_cmd(args: list[str]) -> str:
    try:
        proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=120)
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        return f"returncode={proc.returncode}\nSTDOUT:\n{out}\nSTDERR:\n{err}".strip()
    except Exception as exc:
        return f"error={exc}"


def make_audit(registry: dict[str, Any]) -> str:
    tools = registry.get("tools", [])
    categories = registry.get("tool_categories", {})

    gmail_status = run_cmd([sys.executable, "scripts/run_gmail_operator.py", "--mode", "status", "--profile", "rogger"])
    git_status = run_cmd(["git", "--no-pager", "status", "--short"])
    tags = run_cmd(["git", "tag", "--list", "kos-safe-*"])

    files = {
        "operator_chat": ROOT / "pages" / "KOS_Operator_Chat.py",
        "gmail_operator": ROOT / "scripts" / "run_gmail_operator.py",
        "toolbelt_registry": REGISTRY_PATH,
        "toolbelt_skill": ROOT / "memory" / "kos_skills" / "KOS_SKILL_GOOGLE_AI_TOOLBELT_OPERATOR_V1.md",
        "gmail_status_report": ROOT / "reports" / "KOS_GMAIL_REAL_CONNECTION_STATUS.md",
        "gmail_token_local": ROOT / "local_runtime" / "google_oauth" / "token_gmail_rogger.json",
    }

    lines = [
        "# K-OS Working System Audit",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Google AI Toolbelt",
        "",
        f"Registry status: {registry.get('status')}",
        f"Tools registered: {len(tools)}",
        "",
        "### Categories",
    ]

    for key, value in categories.items():
        lines.append(f"- {key}: {', '.join(value)}")

    lines += [
        "",
        "## Critical files",
    ]

    for name, path in files.items():
        lines.append(f"- {name}: {'present' if path.exists() else 'missing'}")

    lines += [
        "",
        "## Gmail Operator status",
        "",
        "```txt",
        gmail_status,
        "```",
        "",
        "## Git status",
        "",
        "```txt",
        git_status,
        "```",
        "",
        "## Safe tags",
        "",
        "```txt",
        tags,
        "```",
        "",
        "## CTO readout",
        "",
        "- Working: Gmail real connection, Google AI Toolbelt registry, Operator Chat response cleanup, Bau memory structure.",
        "- Prepared: browser-assisted Google Labs workflows through prompt/briefing bridge.",
        "- Not yet automated: Stitch, Pomelli, Opal, Mixboard, Flow, NotebookLM and Antigravity through direct API. Treat as browser-assisted until proven otherwise.",
        "- Next: connect Toolbelt Bridge to Operator Chat.",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="K-OS Google AI Toolbelt Bridge")
    parser.add_argument("--mode", required=True, choices=["audit", "brief", "subsidy-pack"])
    parser.add_argument("--tool", default="")
    parser.add_argument("--project", default="kaizen-home")
    parser.add_argument("--goal", default="Use Google AI tools to produce an executable Kaizen/K-OS asset.")
    args = parser.parse_args()

    registry = load_registry()

    if args.mode == "audit":
        content = make_audit(registry)
        path = write_report("working_audit", content)
        print(json.dumps({"status": "KOS_GOOGLE_AI_TOOLBELT_AUDIT_READY", "report": str(path)}, ensure_ascii=False, indent=2))
        return

    if args.mode == "brief":
        if not args.tool:
            raise SystemExit("--tool required for brief mode")
        content = make_tool_briefing(registry, args.tool, args.project, args.goal)
        path = write_report(f"{args.tool}_briefing", content)
        print(json.dumps({"status": "KOS_GOOGLE_AI_TOOL_BRIEFING_READY", "tool": args.tool, "report": str(path)}, ensure_ascii=False, indent=2))
        return

    if args.mode == "subsidy-pack":
        content = make_subsidy_pack(registry, args.project, args.goal)
        path = write_report("startup_subsidy_pack", content)
        print(json.dumps({"status": "KOS_GOOGLE_STARTUP_SUBSIDY_PACK_READY", "report": str(path)}, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
