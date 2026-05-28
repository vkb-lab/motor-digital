# -*- coding: utf-8 -*-
"""
Teste rápido do kernel K-Atlas OS.
Execute na raiz do projeto:

python smoke_test_kernel.py
"""

from agents.base_agent import AgentContext, BaseAgent
from core.kernel import create_kernel


class EchoAgent(BaseAgent):
    agent_id = "echo_agent"
    name = "Echo Agent"
    description = "Agente simples para teste do kernel."
    version = "0.1.0"
    capabilities = ["echo", "test"]
    permissions = ["agent.execute"]

    def run(self, context: AgentContext):
        return {
            "received_command": context.command,
            "received_payload": context.payload,
            "message": "Kernel K-Atlas OS operacional.",
        }


if __name__ == "__main__":
    kernel = create_kernel()
    kernel.start(load_state=False)

    agent = EchoAgent()
    kernel.register_agent(agent, replace=True)
    result = kernel.execute(
        "echo_agent.ping",
        payload={"source": "smoke_test"},
    )

    print(result.to_dict())
    print(kernel.status())

    kernel.stop(save_state=True)
