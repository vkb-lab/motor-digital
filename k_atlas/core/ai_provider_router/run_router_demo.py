from __future__ import annotations

import json

from .router import AIProviderRouter


if __name__ == "__main__":
    router = AIProviderRouter()
    result = router.route()
    matrix = router.build_matrix()
    print(json.dumps({"route": result, "matrix": matrix}, ensure_ascii=False, indent=2))
