# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


PROTECTED_PATHS = ["core/", "memory/", ".env", ".git/", "secrets", "credentials"]
CRITICAL_PATHS = ["core/kernel.py", "core/router.py", "core/permissions.py", "core/registry.py", "core/events.py"]
DANGEROUS_PATTERNS = ["Remove-Item", "rm -rf", "shutil.rmtree", "os.remove", "subprocess", "eval(", "exec(", "requests.", "socket."]
DESTRUCTIVE_WORDS = ["delete", "remove", "overwrite", "truncate", "drop table", "destroy", "purge"]


def normalize_path(value: str) -> str:
    return str(value).replace("\\", "/").strip()


def analyze_risk(
    target_files: Optional[List[str]] = None,
    proposed_content: str = "",
    patch_text: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    target_files = target_files or []
    metadata = metadata or {}
    normalized_files = [normalize_path(item) for item in target_files]
    text = "\n".join([proposed_content or "", patch_text or "", json.dumps(metadata, ensure_ascii=False)]).lower()

    blockers: List[str] = []
    warnings: List[str] = []
    score = 0

    for path in normalized_files:
        for protected in PROTECTED_PATHS:
            if path.startswith(protected) or protected in path:
                warnings.append("Arquivo em area protegida: " + path)
                score += 20
        if path in CRITICAL_PATHS:
            blockers.append("Arquivo critico do core exige approval especial: " + path)
            score += 40

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in text:
            warnings.append("Padrao sensivel detectado: " + pattern)
            score += 15

    for word in DESTRUCTIVE_WORDS:
        if word in text:
            warnings.append("Linguagem destrutiva detectada: " + word)
            score += 10

    if len(normalized_files) > 5:
        warnings.append("Patch altera muitos arquivos.")
        score += 10

    if not normalized_files:
        warnings.append("Nenhum arquivo alvo informado.")
        score += 5

    score = min(score, 100)

    if blockers:
        level = "blocked"
    elif score >= 70:
        level = "high"
    elif score >= 35:
        level = "medium"
    else:
        level = "low"

    return {
        "success": True,
        "risk_level": level,
        "risk_score": score,
        "blockers": blockers,
        "warnings": warnings,
        "target_files": normalized_files,
        "requires_human_approval": True,
        "can_auto_apply": False,
        "policy": {
            "autoapproval_allowed": False,
            "destructive_changes_allowed": False,
            "core_changes_require_special_approval": True,
        },
    }
