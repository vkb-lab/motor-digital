# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Formatting Utils
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional


def safe_len(value: Any) -> int:
    if isinstance(value, (list, tuple, dict, set)):
        return len(value)
    return 0


def compact_value(value: Any, max_len: int = 180) -> str:
    if value is None:
        return ""

    if isinstance(value, (dict, list, tuple)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text


def to_display_rows(items: Iterable[Dict[str, Any]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        selected_fields = fields or list(item.keys())
        row: Dict[str, Any] = {}

        for field in selected_fields:
            row[field] = compact_value(item.get(field))

        rows.append(row)

    return rows


def get_nested(data: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    current: Any = data

    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)

    if current is None:
        return default

    return current
