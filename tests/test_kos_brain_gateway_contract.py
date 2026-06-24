from scripts.kos_brain_gateway import answer


BANNED = [
    "Human Gate",
    "Safe Action",
    "Action Packet",
    "Registry READY",
    "guardrails ativos",
    "KOS_TOOL_REGISTRY_READY",
    "KOS_CONNECTION_REGISTRY_READY",
    "KOS_TENANT_REGISTRY_READY",
    ".json",
]


def assert_clean(result):
    text = result.user_response
    for term in BANNED:
        assert term not in text


def test_capability_status_response_is_clean():
    result = answer("o que você pode fazer por mim")
    assert_clean(result)
    assert result.technical_evidence["intent"] == "capability_status"


def test_instagram_connected_response_is_clean():
    result = answer("quais instagram estão conectados")
    assert_clean(result)
    assert result.technical_evidence["intent"] == "instagram_operation"


def test_hupmix_last_post_response_is_clean():
    result = answer("revise a última publicação da Hupmix")
    assert_clean(result)
    assert result.technical_evidence["intent"] == "instagram_operation"


def test_email_audit_response_is_clean():
    result = answer("audite meus emails")
    assert_clean(result)
    assert result.technical_evidence["intent"] == "email_operation"


def test_downloads_response_is_clean():
    result = answer("organize meus downloads")
    assert_clean(result)
    assert result.technical_evidence["intent"] == "downloads_operation"


def test_external_action_mentions_confirmation_only_when_needed():
    result = answer("publique isso no instagram")
    assert_clean(result)
    assert "confirmação" in result.user_response.lower() or "confirmacao" in result.user_response.lower()
    assert result.technical_evidence["risk"] == "external_action_requires_confirmation"
