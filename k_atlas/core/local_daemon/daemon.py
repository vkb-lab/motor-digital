from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KAtlasLocalDaemon:
    def __init__(self, state_dir: str | Path = "memory/local_daemon") -> None:
        self.state_dir = Path(state_dir)
        self.logs_dir = self.state_dir / "logs"
        self.heartbeat_path = self.state_dir / "heartbeat.json"
        self.events_path = self.state_dir / "events.jsonl"
        self.pids_path = self.state_dir / "pids.json"
        self.public_url = "https://k-atlas-os.onrender.com"

    def services(self) -> dict[str, dict[str, Any]]:
        return {
            "streamlit": {
                "health_url": "http://127.0.0.1:8501/_stcore/health",
                "command": [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    "app.py",
                    "--server.port",
                    "8501",
                    "--server.address",
                    "0.0.0.0",
                    "--server.headless",
                    "true",
                    "--server.runOnSave",
                    "true",
                    "--server.enableCORS",
                    "false",
                    "--server.enableXsrfProtection",
                    "false",
                ],
            },
            "blackboard_runner": {
                "health_url": "",
                "command": [
                    sys.executable,
                    "-m",
                    "k_atlas.core.blackboard.powershell_runner",
                ],
            },
        }

    def load_pids(self) -> dict[str, Any]:
        if not self.pids_path.exists():
            return {"daemon_pid": os.getpid(), "children": {}}
        try:
            return json.loads(self.pids_path.read_text(encoding="utf-8"))
        except Exception:
            return {"daemon_pid": os.getpid(), "children": {}}

    def save_pids(self, pids: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        pids["daemon_pid"] = os.getpid()
        pids["updated_at"] = utc_now()
        self.pids_path.write_text(json.dumps(pids, ensure_ascii=False, indent=2), encoding="utf-8")

    def process_running(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            if os.name == "nt":
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return str(pid) in result.stdout
            os.kill(pid, 0)
            return True
        except Exception:
            return False

    def health_ok(self, url: str) -> bool:
        if not url:
            return False
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return 200 <= response.status < 500
        except Exception:
            return False

    def start_service(self, name: str, command: list[str]) -> dict[str, Any]:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        out = open(self.logs_dir / f"{name}.out.log", "a", encoding="utf-8")
        err = open(self.logs_dir / f"{name}.err.log", "a", encoding="utf-8")

        flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0

        process = subprocess.Popen(
            command,
            cwd=str(Path.cwd()),
            stdout=out,
            stderr=err,
            creationflags=flags,
        )

        return {
            "status": "started",
            "pid": process.pid,
            "command": " ".join(command),
        }

    def check_service(self, name: str, cfg: dict[str, Any], manage: bool) -> dict[str, Any]:
        pids = self.load_pids()
        children = pids.setdefault("children", {})

        health_url = cfg.get("health_url", "")
        if health_url and self.health_ok(health_url):
            return {"status": "healthy", "health_ok": True}

        old_pid = int(children.get(name, 0) or 0)
        if old_pid and self.process_running(old_pid):
            return {"status": "running", "pid": old_pid, "health_ok": False}

        if not manage:
            return {"status": "not_running_dry_run", "health_ok": False}

        started = self.start_service(name, cfg["command"])
        children[name] = started["pid"]
        self.save_pids(pids)
        return started

    def check_public(self) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(self.public_url, timeout=8) as response:
                return {"status": "reachable", "ok": True, "http_status": response.status, "url": self.public_url}
        except Exception as exc:
            return {"status": "unreachable", "ok": False, "url": self.public_url, "error": str(exc)}

    def git_status(self) -> dict[str, Any]:
        def run(args: list[str]) -> dict[str, Any]:
            try:
                result = subprocess.run(args, cwd=str(Path.cwd()), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45)
                return {"ok": result.returncode == 0, "stdout": result.stdout[-3000:], "stderr": result.stderr[-3000:]}
            except Exception as exc:
                return {"ok": False, "stdout": "", "stderr": str(exc)}

        return {
            "branch": run(["git", "branch", "--show-current"]),
            "status": run(["git", "status", "--short"]),
            "fetch": run(["git", "fetch", "origin", "main"]),
        }

    def write_heartbeat(self, data: dict[str, Any]) -> dict[str, Any]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), **data}
        self.heartbeat_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def tick(self, manage: bool = False) -> dict[str, Any]:
        service_states = {}
        for name, cfg in self.services().items():
            service_states[name] = self.check_service(name, cfg, manage=manage)

        return self.write_heartbeat({
            "checkpoint": "41",
            "daemon": "k_atlas_local_daemon",
            "status": "running",
            "manage_processes": manage,
            "services": service_states,
            "public": self.check_public(),
            "git": self.git_status(),
            "guardrails": [
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem mensagem em massa",
                "sem token em texto puro",
                "sem API externa real",
            ],
        })

    def run_forever(self) -> None:
        print("K-Atlas Local Daemon 24/7 iniciado.")
        print("Sem navegador automatico. Pressione Ctrl+C para parar.")
        while True:
            result = self.tick(manage=True)
            print(json.dumps({
                "timestamp": result["timestamp"],
                "streamlit": result["services"]["streamlit"]["status"],
                "runner": result["services"]["blackboard_runner"]["status"],
                "public": result["public"]["status"],
            }, ensure_ascii=False))
            time.sleep(20)
