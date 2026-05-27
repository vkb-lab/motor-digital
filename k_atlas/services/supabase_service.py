from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_task(title, instruction, risk_level="low", requires_approval=False):
    return supabase.table("k_tasks").insert({
        "title": title,
        "instruction": instruction,
        "status": "pending",
        "risk_level": risk_level,
        "requires_approval": requires_approval
    }).execute()


def get_pending_tasks():
    return supabase.table("k_tasks").select("*").eq("status", "pending").execute()


def update_task_status(task_id, status, result=None):
    data = {
        "status": status
    }

    if result is not None:
        data["result"] = result

    if status in ["done", "failed"]:
        data["executed_at"] = "now()"

    return supabase.table("k_tasks").update(data).eq("id", task_id).execute()


def save_report(title, content):
    return supabase.table("k_reports").insert({
        "title": title,
        "content": content
    }).execute()