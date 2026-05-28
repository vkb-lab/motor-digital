# -*- coding: utf-8 -*-
from __future__ import annotations

import difflib
from pathlib import Path


def generate_unified_diff(original_content: str, proposed_content: str, fromfile: str = "original", tofile: str = "proposed") -> str:
    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        proposed_content.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile,
        lineterm="",
    )
    return "\n".join(diff)


def generate_file_diff(target_file: str | Path, proposed_content: str, root_path: str | Path | None = None) -> str:
    base_root = Path(root_path) if root_path else Path.cwd()
    target_path = Path(target_file)

    if not target_path.is_absolute():
        target_path = base_root / target_path

    if target_path.exists():
        original_content = target_path.read_text(encoding="utf-8", errors="replace")
    else:
        original_content = ""

    return generate_unified_diff(
        original_content=original_content,
        proposed_content=proposed_content,
        fromfile=str(target_path),
        tofile=str(target_path) + " proposed",
    )


def save_diff(diff_text: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(diff_text, encoding="utf-8")
    return path
