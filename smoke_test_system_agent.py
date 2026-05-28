# -*- coding: utf-8 -*-
"""
Smoke test do SystemAgent.

Execute:
python smoke_test_system_agent.py
"""

from agents.system_agent import SystemAgent
from core.kernel import create_kernel


if __name__ == "__main__":
    kernel = create_kernel()
    kernel.start(load_state=False)

    system_agent = SystemAgent(kernel=kernel)
    kernel.register_agent(system_agent, replace=True, roles=["system"])

    result_ping = kernel.execute("system_agent.ping")
    result_status = kernel.execute("system_agent.status")
    result_agents = kernel.execute("system_agent.agents")
    result_permissions = kernel.execute(
        "system_agent.permissions",
        payload={"agent_id": "system_agent"},
    )

    print("PING:")
    print(result_ping.to_dict())

    print("STATUS:")
    print(result_status.to_dict())

    print("AGENTS:")
    print(result_agents.to_dict())

    print("PERMISSIONS:")
    print(result_permissions.to_dict())

    kernel.stop(save_state=True)
