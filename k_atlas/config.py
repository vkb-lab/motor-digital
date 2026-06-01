"""Runtime configuration for local K-OS execution."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .paths import ROOT_DIR


@dataclass(frozen=True)
class KOSConfig:
    app_name: str = "K-Atlas OS"
    environment: str = os.getenv("KOS_ENV", "local")
    root_dir: str = str(ROOT_DIR)
    external_api_enabled: bool = bool(os.getenv("KOS_EXTERNAL_API_KEY"))


def get_config() -> KOSConfig:
    return KOSConfig()

