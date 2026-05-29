from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path
from typing import Any

from .blackboard_store import BlackboardStore
from .command_policy import evaluate_command


class PowerShellCommandRunner:
    def __init__(
        self,
        store: BlackboardStore | None = None,
        project_root: str | Path = ".",
        timeout_seconds: int = 180,
    ) -> None:
        self.store = store or BlackboardStore()
        self.project_root = Path(project_root).resolve()
        self.timeout_seconds = timeout_seconds

    def run_once(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        commands = self.store.commands.load()

        for item in commands:
            if item.get("approval_status") != "approved":
                continue

            if item.get("execution_status") not in {"pending_execution", "waiting_execution"}:
                continue

            command_id = str(item["command_id"])
            command = str(item["command"])

            policy = evaluate_command(command)
            if not policy.ok:
                result = {
                    "ok": False,
                    "status": "blocked_by_policy",
                    "command": command,
                    "policy": policy.to_dict(),
                }
                self.store.add_result(command_id, result)
                self.store.mark_finished(command_id, False, result)
                results.append(result)
                continue

            self.store.mark_running(command_id)

            try:
                completed = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout_seconds,
                )

                ok = completed.returncode == 0
                result = {
                    "ok": ok,
                    "status": "finished" if ok else "failed",
                    "returncode": completed.returncode,
                    "command": command,
                    "stdout": completed.stdout[-12000:],
                    "stderr": completed.stderr[-12000:],
                }

            except subprocess.TimeoutExpired as exc:
                result = {
                    "ok": False,
                    "status": "timeout",
                    "command": command,
                    "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
                    "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
                }

            self.store.add_result(command_id, result)
            self.store.mark_finished(command_id, bool(result["ok"]), result)
            results.append(result)

        return results

    def loop(self, interval_seconds: int = 10) -> None:
        while True:
            self.run_once()
            time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    runner = PowerShellCommandRunner(project_root=args.project_root)

    if args.once:
        results = runner.run_once()
        print(f"commands_processed={len(results)}")
    else:
        print("K-Atlas Blackboard PowerShell Runner ativo.")
        print("Aguardando comandos aprovados em memory/blackboard/command_queue.json")
        runner.loop(interval_seconds=args.interval)


if __name__ == "__main__":
    main()