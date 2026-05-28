# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Components
"""

from __future__ import annotations

from typing import Any, Dict, List


def render_metric_grid(st: Any, metrics: List[Dict[str, Any]]) -> None:
    if not metrics:
        return

    columns = st.columns(min(len(metrics), 4))

    for index, metric in enumerate(metrics):
        column = columns[index % len(columns)]
        column.metric(
            label=str(metric.get("label", "")),
            value=metric.get("value", ""),
            delta=metric.get("delta"),
        )


def render_command_health(st: Any, commands: Dict[str, Dict[str, Any]]) -> None:
    rows = []

    for name, result in commands.items():
        rows.append(
            {
                "command": name,
                "success": result.get("success"),
                "agent_id": result.get("agent_id"),
                "action": result.get("action"),
                "error": result.get("error"),
                "created_at": result.get("created_at"),
            }
        )

    st.dataframe(rows, use_container_width=True)
