REQUIREMENTS = {
    "instagram": ["INSTAGRAM_ACCOUNT_ID", "META_ACCESS_KEY"],
    "meta_ads": ["META_AD_ACCOUNT_ID", "META_ACCESS_KEY"],
    "facebook_page": ["FACEBOOK_PAGE_ID", "META_ACCESS_KEY"],
    "google_business": ["GOOGLE_BUSINESS_ACCOUNT_ID", "GOOGLE_BUSINESS_LOCATION_ID"],
    "whatsapp_business": ["WHATSAPP_BUSINESS_ACCOUNT_ID", "WHATSAPP_ACCESS_KEY"],
    "gmail": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_KEY"],
    "google_calendar": ["GOOGLE_CALENDAR_ID"],
    "github": ["GITHUB_KEY"],
    "vercel": ["VERCEL_KEY"],
    "streamlit_cloud": [],
    "stripe": ["STRIPE_KEY", "STRIPE_WEBHOOK_KEY"],
}

def get_requirements(platform: str):
    return REQUIREMENTS.get(platform, [])
