from k_atlas.artifact_builder import build_artifacts
from k_atlas.artifact_validator import validate_artifacts
from k_atlas.execution_receipts import create_execution_receipt
from k_atlas.whiteboard.board_model import build_board
from k_atlas.whiteboard.board_store import save_board
from k_atlas.final_review_console import build_final_review
from k_atlas.autonomous_executor.result_collector import collect_results
from k_atlas.autonomous_executor.job_state import save_job_state

def run_job(job: dict):
    board = build_board(job)
    save_board(board)

    artifacts = build_artifacts(job["client_id"], job["job_id"])
    validation = validate_artifacts(artifacts)

    receipts = []
    for task in job.get("tasks", []):
        receipts.append(create_execution_receipt(job["job_id"], job["client_id"], task["task_id"], task.get("status", "PENDING_APPROVAL")))

    job["artifact_validation"] = validation
    job["status"] = "PENDING_FINAL_APPROVAL"
    save_job_state(job)

    final_review = build_final_review({
        "client_id": job["client_id"],
        "status": "PENDING_FINAL_APPROVAL",
        "job_id": job["job_id"],
        "artifacts": artifacts,
        "artifact_validation": validation,
    })

    return collect_results(job, artifacts, receipts, final_review)
