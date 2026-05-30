from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SandboxProvider:
    provider_id: str
    name: str
    category: str
    operations: list[str] = field(default_factory=list)
    required_vault_refs_future: list[str] = field(default_factory=list)
    real_api_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_provider_registry() -> dict[str, SandboxProvider]:
    providers = [
        SandboxProvider(
            provider_id="google_ai_sandbox",
            name="Google AI Sandbox",
            category="creative_media",
            operations=[
                "plan_image_generation",
                "plan_video_generation",
                "validate_prompt_pack",
            ],
            required_vault_refs_future=[
                "vault://env/GOOGLE_AI_API_KEY",
            ],
        ),
        SandboxProvider(
            provider_id="meta_graph_sandbox",
            name="Meta Graph Sandbox",
            category="social",
            operations=[
                "plan_instagram_post",
                "plan_reel_upload",
                "validate_media_container",
            ],
            required_vault_refs_future=[
                "vault://env/META_GRAPH_ACCESS_TOKEN",
            ],
        ),
        SandboxProvider(
            provider_id="whatsapp_cloud_sandbox",
            name="WhatsApp Cloud Sandbox",
            category="messaging",
            operations=[
                "plan_template_message",
                "validate_consent_payload",
                "simulate_single_message",
            ],
            required_vault_refs_future=[
                "vault://env/WHATSAPP_CLOUD_API_TOKEN",
            ],
        ),
        SandboxProvider(
            provider_id="email_sandbox",
            name="Email Sandbox",
            category="email",
            operations=[
                "plan_email_campaign",
                "validate_unsubscribe_policy",
                "simulate_single_email",
            ],
            required_vault_refs_future=[
                "vault://env/EMAIL_PROVIDER_API_KEY",
            ],
        ),
    ]

    return {provider.provider_id: provider for provider in providers}
