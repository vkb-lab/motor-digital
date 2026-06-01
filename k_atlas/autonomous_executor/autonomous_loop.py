from datetime import datetime, timezone
from k_atlas.executive_planner import build_executive_plan
from k_atlas.autonomous_executor.job_model import AutonomousJob
from k_atlas.autonomous_executor.job_queue import enqueue_job
from k_atlas.autonomous_executor.job_runner import run_job

def create_job_from_command(command: str):
    plan = build_executive_plan(command)
    job_id = "job_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    job = AutonomousJob(
        job_id=job_id,
        client_id=plan["client_id"],
        command=command,
        tasks=plan["tasks"],
    ).to_dict()
    job["plan"] = plan
    enqueue_job(job)
    return job

def run_autonomous_command(command: str):
    job = create_job_from_command(command)
    return run_job(job)
