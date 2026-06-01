PLATFORMS = [
    "instagram",
    "meta_ads",
    "facebook_page",
    "google_business",
    "whatsapp_business",
    "gmail",
    "google_calendar",
    "github",
    "vercel",
    "streamlit_cloud",
    "stripe",
]

def list_platforms():
    return [{"platform": p, "real_actions_enabled": False} for p in PLATFORMS]
