from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .permission_model import ChannelPermission, default_channel_permissions


@dataclass(frozen=True)
class ChannelDefinition:
    name: str
    label: str
    kind: str
    environment: str
    adapter_name: str
    enabled: bool
    permission: ChannelPermission
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["permission"]["allowed_levels"] = [level.value for level in self.permission.allowed_levels]
        return data


class ChannelRegistry:
    def __init__(self) -> None:
        self._channels: dict[str, ChannelDefinition] = {}

    def register(self, definition: ChannelDefinition) -> None:
        if not definition.name:
            raise ValueError("Channel name is required")
        self._channels[definition.name] = definition

    def get(self, name: str) -> ChannelDefinition:
        if name not in self._channels:
            raise KeyError(f"Canal nao registrado: {name}")
        return self._channels[name]

    def list_channels(self) -> list[ChannelDefinition]:
        return [self._channels[key] for key in sorted(self._channels)]

    def permission_map(self) -> dict[str, ChannelPermission]:
        return {name: channel.permission for name, channel in self._channels.items()}

    def to_dict(self) -> dict[str, Any]:
        return {channel.name: channel.to_dict() for channel in self.list_channels()}


def build_default_channel_registry() -> ChannelRegistry:
    permissions = default_channel_permissions()
    registry = ChannelRegistry()

    registry.register(ChannelDefinition(
        name="dry_run",
        label="Dry Run Local",
        kind="internal",
        environment="local",
        adapter_name="dry_run_adapter",
        enabled=True,
        permission=permissions["dry_run"],
        metadata={"side_effects": "none", "external_api": False},
    ))

    registry.register(ChannelDefinition(
        name="test_page",
        label="Pagina de Teste Local",
        kind="sandbox_page",
        environment="local_sandbox",
        adapter_name="test_page_adapter",
        enabled=True,
        permission=permissions["test_page"],
        metadata={"side_effects": "local_jsonl_only", "external_api": False},
    ))

    registry.register(ChannelDefinition(
        name="instagram_sandbox",
        label="Instagram Sandbox",
        kind="social",
        environment="sandbox",
        adapter_name="future_instagram_adapter",
        enabled=False,
        permission=permissions["instagram_sandbox"],
        metadata={"requires_vault": True, "real_publish": False},
    ))

    registry.register(ChannelDefinition(
        name="whatsapp_sandbox",
        label="WhatsApp Sandbox",
        kind="messaging",
        environment="sandbox",
        adapter_name="future_whatsapp_adapter",
        enabled=False,
        permission=permissions["whatsapp_sandbox"],
        metadata={"requires_vault": True, "mass_messaging": False},
    ))

    registry.register(ChannelDefinition(
        name="email_sandbox",
        label="E-mail Sandbox",
        kind="email",
        environment="sandbox",
        adapter_name="future_email_adapter",
        enabled=False,
        permission=permissions["email_sandbox"],
        metadata={"requires_vault": True, "mass_messaging": False},
    ))

    registry.register(ChannelDefinition(
        name="instagram_official",
        label="Instagram Oficial Bloqueado",
        kind="social",
        environment="production_locked",
        adapter_name="future_instagram_adapter",
        enabled=False,
        permission=permissions["instagram_official"],
        metadata={"real_publish": False, "reason": "requires_level_4_governance"},
    ))

    registry.register(ChannelDefinition(
        name="whatsapp_official",
        label="WhatsApp Oficial Bloqueado",
        kind="messaging",
        environment="production_locked",
        adapter_name="future_whatsapp_adapter",
        enabled=False,
        permission=permissions["whatsapp_official"],
        metadata={"real_publish": False, "mass_messaging": False},
    ))

    registry.register(ChannelDefinition(
        name="email_official",
        label="E-mail Oficial Bloqueado",
        kind="email",
        environment="production_locked",
        adapter_name="future_email_adapter",
        enabled=False,
        permission=permissions["email_official"],
        metadata={"real_publish": False, "mass_messaging": False},
    ))

    return registry