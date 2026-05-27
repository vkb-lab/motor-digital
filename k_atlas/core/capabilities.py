from k_atlas.core.secrets_manager import get_secret


def configured(key: str) -> bool:
    value = get_secret(key)
    return bool(value and value.strip())


def capability_status():
    return {
        "ai_brain": configured("GEMINI_API_KEY"),
        "supabase_basic": configured("SUPABASE_URL") and configured("SUPABASE_ANON_KEY"),
        "supabase_admin": configured("SUPABASE_SERVICE_ROLE_KEY"),
        "github_write": configured("GITHUB_TOKEN"),
        "meta_app": configured("META_CLIENT_ID") and configured("META_CLIENT_SECRET") and configured("META_VERIFY_TOKEN"),
        "instagram_publish": configured("INSTAGRAM_ACCESS_TOKEN"),
        "google_oauth": configured("GOOGLE_CLIENT_ID") and configured("GOOGLE_CLIENT_SECRET"),
        "gmail_oauth": (
            configured("GMAIL_CLIENT_ID") and configured("GMAIL_CLIENT_SECRET")
        ) or (
            configured("GOOGLE_CLIENT_ID") and configured("GOOGLE_CLIENT_SECRET")
        ),
    }


def print_capabilities():
    print("")
    print("🧭 CAPACIDADES K-ATLAS")
    print("")
    for name, ok in capability_status().items():
        icon = "✅" if ok else "⚠️"
        print(f"{icon} {name}")
    print("")


if __name__ == "__main__":
    print_capabilities()
