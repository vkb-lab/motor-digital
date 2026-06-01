from datetime import datetime, timezone

def build_deploy_manifest():
    return {
        "status": "PRODUCTION_BRIDGE_READY",
        "phase": 10,
        "target": "vercel_preview",
        "app": "k-atlas-os",
        "public_bridge": True,
        "real_publish_enabled": False,
        "real_money_enabled": False,
        "external_call_executed": False,
        "manual_review_required": True,
        "modules": [
            "launch_sandbox",
            "safe_execution",
            "live_onboarding",
            "deploy_bridge"
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
