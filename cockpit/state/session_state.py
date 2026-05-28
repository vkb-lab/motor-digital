# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Session State
"""

from __future__ import annotations

from typing import Any


def init_session_state(st: Any) -> None:
    defaults = {
        "k_atlas_cockpit_loaded": True,
        "selected_agent_id": None,
        "selected_task_id": None,
        "selected_memory_id": None,
        "selected_learning_item": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
