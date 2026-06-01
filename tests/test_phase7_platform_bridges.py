from integrations.instagram.publishing_gate import prepare_action as instagram_action
from integrations.meta.ads_gate import prepare_action as meta_action
from integrations.google_business.edit_gate import prepare_action as google_action
from integrations.whatsapp.message_gate import prepare_action as whatsapp_action
from integrations.stripe.payment_gate import prepare_action as stripe_action

def test_bridges_safe():
    for fn in [instagram_action, meta_action, google_action, whatsapp_action, stripe_action]:
        result = fn("parada_atlantida", "dry_run", {})
        assert result["status"] == "PENDING_APPROVAL"
        assert result["external_call_executed"] is False
