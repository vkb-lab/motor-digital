from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_task(title, instruction):
    data = {
        "title": title,
        "instruction": instruction,
        "status": "pending"
    }

    return supabase.table("k_tasks").insert(data).execute()

def get_pending_tasks():
    return (
        supabase
        .table("k_tasks")
        .select("*")
        .eq("status", "pending")
        .execute()
    )

def save_report(title, content):
    data = {
        "title": title,
        "content": content
    }

    return supabase.table("k_reports").insert(data).execute()