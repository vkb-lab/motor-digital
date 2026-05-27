from datetime import datetime
from k_atlas.services.supabase_service import supabase


def insert_memory(title, content, category="commercial"):
    return supabase.table("k_memories").insert({
        "title": title,
        "content": content,
        "category": category,
        "source": "k_atlas",
        "created_at": datetime.now().isoformat()
    }).execute()


def insert_product(name, category="", price="", metadata=None):
    metadata = metadata or {}

    content = {
        "name": name,
        "category": category,
        "price": price,
        "metadata": metadata
    }

    return supabase.table("k_memories").insert({
        "title": f"Produto: {name}",
        "content": str(content),
        "category": "product",
        "source": "product_engine",
        "created_at": datetime.now().isoformat()
    }).execute()


def insert_report(title, content):
    return supabase.table("k_reports").insert({
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat()
    }).execute()


def list_memories(limit=10):
    return (
        supabase
        .table("k_memories")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )


def list_reports(limit=10):
    return (
        supabase
        .table("k_reports")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )


if __name__ == "__main__":
    print("K-Atlas Database Layer ativo.")

    result = list_memories(3)

    print(result)