from k_atlas.multiclient_registry import resolve_client_id
from k_atlas.task_decomposer import decompose_command
from k_atlas.agent_assignment import assign_agent
from k_atlas.operation_router import route_operation

def build_executive_plan(command: str):
    client_id = resolve_client_id(command)
    tasks = decompose_command(command, client_id)
    enriched = []
    for task in tasks:
        item = dict(task)
        item["assignment"] = assign_agent(task)
        item["route"] = route_operation(task)
        enriched.append(item)
    return {
        "status": "PENDING_APPROVAL",
        "client_id": client_id,
        "command": command,
        "tasks": enriched,
        "external_call_executed": False,
        "manual_approval_required": True,
    }
