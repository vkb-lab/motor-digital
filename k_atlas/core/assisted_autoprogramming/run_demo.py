from __future__ import annotations

import json

from .kernel import AssistedAutoprogrammingKernel


if __name__ == "__main__":
    kernel = AssistedAutoprogrammingKernel()
    result = kernel.create_proposal({
        "checkpoint": "65",
        "action": "create_module",
        "objective": "Criar trilho de autoprogramacao assistida com proposta, validacao, pacote e aprovacao humana antes de aplicar alteracoes reais.",
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "browser_automation": False,
        "mouse_automation": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
