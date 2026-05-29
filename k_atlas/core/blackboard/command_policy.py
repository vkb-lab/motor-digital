from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BLOCKED_PATTERNS = [
    " format ",
    "format.com",
    "shutdown",
    "restart-computer",
    "stop-computer",
    "remove-item -recurse",
    "rm -r",
    "rmdir /s",
    "del /s",
    "erase /s",
    "set-executionpolicy unrestricted",
    "invoke-expression",
    "iex ",
    "start-bitstransfer",
    "net user",
    "reg delete",
    "cipher /w",
    "access_token",
    "api_key",
    "password",
    "secret",
]

ALLOWED_PREFIXES = [
    "git status",
    "git log",
    "git add",
    "git commit",
    "git push origin main",
    "python -m",
    ".\\venv\\scripts\\python.exe -m",
    ".\\.venv\\scripts\\python.exe -m",
    "py -3 -m",
    "powershell -executionpolicy bypass -file",
    "dir",
    "get-childitem",
    "test-path",
    "write-host",
]


@dataclass(frozen=True)
class CommandPolicyResult:
    ok: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reasons": list(self.reasons),
        }


def normalize_command(command: str) -> str:
    return " ".join(command.strip().lower().split())


def evaluate_command(command: str) -> CommandPolicyResult:
    normalized = normalize_command(command)

    if not normalized:
        return CommandPolicyResult(False, ["empty_command"])

    blocked = [pattern.strip() for pattern in BLOCKED_PATTERNS if pattern.strip() in normalized]
    if blocked:
        return CommandPolicyResult(False, ["blocked_pattern:" + ",".join(blocked)])

    if "\n" in command.strip() or "\r" in command.strip():
        return CommandPolicyResult(False, ["single_line_commands_only"])

    allowed = any(normalized.startswith(prefix) for prefix in ALLOWED_PREFIXES)
    if not allowed:
        return CommandPolicyResult(False, ["command_prefix_not_allowed"])

    return CommandPolicyResult(True, ["command_allowed"])