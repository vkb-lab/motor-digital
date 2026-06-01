from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_google_business_profile_dry_run():
    from integrations.google_business.google_business_client import GoogleBusinessClient

    result = GoogleBusinessClient(client_id="parada_atlantida", dry_run=True).profile_dry_run()

    assert result["status"] == "PENDING_APPROVAL"
    assert result["mode"] == "DRY_RUN"
    assert result["provider"] == "google_business"
    assert result["client_id"] == "parada_atlantida"
    assert result["external_call_executed"] is False
    assert Path(result["receipt_path"]).exists()


def test_google_business_posts_offer_and_review_dry_run():
    from integrations.google_business.google_business_client import GoogleBusinessClient

    client = GoogleBusinessClient(client_id="parada_atlantida", dry_run=True)

    post = client.create_post()
    offer = client.create_offer()
    review = client.reply_review()

    for item in [post, offer, review]:
        assert item["status"] == "PENDING_APPROVAL"
        assert item["mode"] == "DRY_RUN"
        assert item["client_id"] == "parada_atlantida"
        assert item["external_call_executed"] is False
        assert Path(item["receipt_path"]).exists()


def test_google_business_full_dry_run_bundle():
    from integrations.google_business.google_business_client import create_google_business_dry_run

    bundle = create_google_business_dry_run("parada_atlantida")
    assert bundle["status"] == "PENDING_APPROVAL"
    assert bundle["mode"] == "DRY_RUN"
    assert bundle["client_id"] == "parada_atlantida"
    assert "profile" in bundle
    assert "post" in bundle
    assert "offer" in bundle
    assert "review_reply" in bundle
