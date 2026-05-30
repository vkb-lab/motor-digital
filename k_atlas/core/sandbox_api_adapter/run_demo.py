from __future__ import annotations

import json

from .adapter import SandboxAPIAdapter


def main() -> int:
    adapter = SandboxAPIAdapter()

    result = adapter.execute(
        provider_id="google_ai_sandbox",
        operation="plan_video_generation",
        payload={
            "objective": "Criar vídeo vertical 9:16 do K-Atlas OS em operação.",
            "external_api_enabled": False,
            "official_publish": False,
            "auto_publish": False,
            "real_network": False,
        },
        requested_by="demo",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
