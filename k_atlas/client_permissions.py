from pathlib import Path
import json
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]

ALIASES = {
    "pode_criar_campanha": ["pode_criar_campanha", "pode_criar_campanhas", "can_create_campaigns"],
    "pode_criar_campanhas": ["pode_criar_campanhas", "pode_criar_campanha", "can_create_campaigns"],

    "pode_criar_post": ["pode_criar_post", "pode_criar_posts"],
    "pode_criar_posts": ["pode_criar_posts", "pode_criar_post"],

    "pode_criar_landing_page": ["pode_criar_landing_page", "pode_criar_landing_pages", "can_create_landing_pages"],
    "pode_criar_landing_pages": ["pode_criar_landing_pages", "pode_criar_landing_page", "can_create_landing_pages"],

    "pode_criar_qr_code": ["pode_criar_qr_code", "pode_criar_qr_codes", "can_create_qr_codes"],
    "pode_criar_qr_codes": ["pode_criar_qr_codes", "pode_criar_qr_code", "can_create_qr_codes"],

    "pode_criar_atendente": ["pode_criar_atendente", "pode_criar_atendentes", "can_create_attendants"],
    "pode_criar_atendentes": ["pode_criar_atendentes", "pode_criar_atendente", "can_create_attendants"],

    "pode_classificar_lead": ["pode_classificar_lead", "pode_classificar_leads"],
    "pode_classificar_leads": ["pode_classificar_leads", "pode_classificar_lead"],

    "pode_criar_saas": ["pode_criar_saas", "pode_criar_saas_projects", "can_create_saas_projects"],
    "pode_criar_saas_projects": ["pode_criar_saas_projects", "pode_criar_saas", "can_create_saas_projects"],

    "pode_criar_anuncio_dry_run": ["pode_criar_anuncio_dry_run"],

    "pode_sugerir_edicao_google_maps": ["pode_sugerir_edicao_google_maps"],
    "pode_sugerir_bio_instagram": ["pode_sugerir_bio_instagram"],

    "pode_publicar_externo": ["pode_publicar_externo", "can_publish_external"],
    "pode_editar_google_real": ["pode_editar_google_real", "can_edit_google_real"],
    "pode_enviar_dm_real": ["pode_enviar_dm_real", "can_send_dm_real"],
    "pode_criar_anuncio_real": ["pode_criar_anuncio_real", "can_create_real_ads"],
    "pode_cobrar_dinheiro_real": ["pode_cobrar_dinheiro_real", "can_charge_real_money"],
}


def permissions_path(client_id: str) -> Path:
    return ROOT / "clients" / client_id / "permissions.json"


def load_client_permissions(client_id: str) -> Dict[str, Any]:
    path = permissions_path(client_id)
    if not path.exists():
        raise FileNotFoundError(f"permissions.json nao encontrado para {client_id}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_permissions(client_id: str) -> Dict[str, Any]:
    return load_client_permissions(client_id)


def get_client_permissions(client_id: str) -> Dict[str, Any]:
    return load_client_permissions(client_id)


def get_permissions(client_id: str) -> Dict[str, Any]:
    return load_client_permissions(client_id)


def normalize_permission(permission: str) -> str:
    return str(permission or "").strip()


def has_client_permission(client_id: str, permission: str) -> bool:
    permission = normalize_permission(permission)
    data = load_client_permissions(client_id)

    keys = ALIASES.get(permission, [permission])
    for key in keys:
        if data.get(key) is True:
            return True

    return False


def has_permission(client_id: str, permission: str) -> bool:
    return has_client_permission(client_id, permission)


def check_client_permission(client_id: str, permission: str) -> Dict[str, Any]:
    allowed = has_client_permission(client_id, permission)
    return {
        "client_id": client_id,
        "permission": permission,
        "allowed": allowed,
        "status": "ALLOWED" if allowed else "DENIED",
        "manual_approval_required": True,
    }


def check_permission(client_id: str, permission: str) -> Dict[str, Any]:
    return check_client_permission(client_id, permission)


def require_client_permission(client_id: str, permission: str) -> Dict[str, Any]:
    result = check_client_permission(client_id, permission)
    if not result["allowed"]:
        raise PermissionError(f"Client {client_id} does not allow {permission}")
    return result


def require_permission(client_id: str, permission: str) -> Dict[str, Any]:
    return require_client_permission(client_id, permission)


def assert_client_permission(client_id: str, permission: str) -> Dict[str, Any]:
    return require_client_permission(client_id, permission)


class ClientPermissionManager:
    def load(self, client_id: str) -> Dict[str, Any]:
        return load_client_permissions(client_id)

    def load_permissions(self, client_id: str) -> Dict[str, Any]:
        return load_client_permissions(client_id)

    def has_permission(self, client_id: str, permission: str) -> bool:
        return has_client_permission(client_id, permission)

    def check(self, client_id: str, permission: str) -> Dict[str, Any]:
        return check_client_permission(client_id, permission)

    def require(self, client_id: str, permission: str) -> Dict[str, Any]:
        return require_client_permission(client_id, permission)
