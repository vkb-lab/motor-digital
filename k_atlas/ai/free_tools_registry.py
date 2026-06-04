from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "config" / "free_ai_tools_catalog.json"

def _cmd_version(cmd: str) -> dict:
    exe = shutil.which(cmd)
    if not exe:
        return {"installed": False, "path": ""}
    try:
        p = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=8)
        return {
            "installed": True,
            "path": exe,
            "version_output": ((p.stdout or "") + (p.stderr or "")).strip()[:400]
        }
    except Exception as exc:
        return {"installed": True, "path": exe, "version_output": str(exc)}

def load_catalog() -> dict:
    if CATALOG_PATH.exists():
        return json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    return {"tools": {}}

def detect_free_tools() -> dict:
    return {
        "ollama": _cmd_version("ollama"),
        "python": _cmd_version("python"),
        "git": _cmd_version("git"),
        "node": _cmd_version("node"),
        "npm": _cmd_version("npm"),
        "docker": _cmd_version("docker")
    }

if __name__ == "__main__":
    print(json.dumps({
        "catalog": load_catalog(),
        "detected": detect_free_tools()
    }, ensure_ascii=False, indent=2))
