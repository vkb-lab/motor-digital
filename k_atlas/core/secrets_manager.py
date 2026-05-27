from pathlib import Path
from dotenv import load_dotenv
import os


BASE = Path.cwd()
ENV_PATH = BASE / ".env"

SECRET_KEYS = [
    "GEMINI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "GITHUB_TOKEN",
    "META_CLIENT_ID",
    "META_CLIENT_SECRET",
    "META_VERIFY_TOKEN",
    "INSTAGRAM_ACCESS_TOKEN",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GMAIL_CLIENT_ID",
    "GMAIL_CLIENT_SECRET",
]


def load_secrets():
    load_dotenv(ENV_PATH)
    return {key: os.getenv(key, "") for key in SECRET_KEYS}


def is_set(value: str) -> bool:
    return bool(value and value.strip())


def mask(value: str) -> str:
    if not is_set(value):
        return "NÃO CONFIGURADO"
    if len(value) <= 8:
        return "CONFIGURADO"
    return value[:4] + "..." + value[-4:]


def secrets_status():
    secrets = load_secrets()
    return {
        key: {
            "configured": is_set(value),
            "masked": mask(value),
        }
        for key, value in secrets.items()
    }


def get_secret(key: str, default: str = ""):
    secrets = load_secrets()
    return secrets.get(key, default)


def print_status():
    status = secrets_status()
    print("")
    print("🔐 STATUS DOS SECRETS K-ATLAS")
    print("")
    for key, info in status.items():
        icon = "✅" if info["configured"] else "⚠️"
        print(f"{icon} {key}: {info['masked']}")
    print("")
    print("Arquivo usado:")
    print(ENV_PATH)
    print("")


if __name__ == "__main__":
    print_status()
