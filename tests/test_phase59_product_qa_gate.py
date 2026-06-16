from k_atlas.product_factory.product_qa_gate import evaluate_product_record, build_product_qa_report

def _safe_product():
    return {
        "product_id": "KOS-PRODUCT-TEST",
        "slug": "safe-product",
        "title": "Safe Product",
        "product_type": "saas",
        "path": "products/safe-product",
        "files_count": 5,
        "has_readme": True,
        "has_tests": True,
        "has_policy": True,
        "suspicious_files": [],
        "safe": True,
        "execution_allowed": False,
        "deploy_allowed": False,
        "paid_ai_allowed": False,
        "instagram_publish_allowed": False,
        "external_publish_allowed": False,
    }

def test_product_qa_passes_safe_product():
    result = evaluate_product_record(_safe_product())

    assert result["status"] == "PRODUCT_QA_PASS"
    assert result["score"] == 100
    assert result["execution_allowed"] is False
    assert result["deploy_allowed"] is False
    assert result["paid_ai_allowed"] is False
    assert result["instagram_publish_allowed"] is False
    assert result["external_publish_allowed"] is False
    assert result["real_action_executed"] is False

def test_product_qa_detects_missing_structure():
    product = _safe_product()
    product["has_policy"] = False
    product["has_tests"] = False

    result = evaluate_product_record(product)

    assert result["status"] == "PRODUCT_QA_ATTENTION_REQUIRED"
    assert result["checks_failed"] >= 2
    assert result["human_review_required"] is True
    assert result["auto_fix_allowed"] is False

def test_product_qa_detects_critical_suspicious_files():
    product = _safe_product()
    product["safe"] = False
    product["suspicious_files"] = [".env"]

    result = evaluate_product_record(product)

    assert result["status"] == "PRODUCT_QA_CRITICAL"
    assert result["critical_failed_count"] >= 1
    assert ".env" in result["suspicious_files"]
    assert result["real_action_executed"] is False

def test_product_qa_report_is_read_only():
    registry = {
        "snapshot": {
            "products": [
                _safe_product(),
                {
                    **_safe_product(),
                    "product_id": "bad",
                    "slug": "bad-product",
                    "safe": False,
                    "suspicious_files": ["credentials.json"],
                }
            ]
        }
    }

    report = build_product_qa_report(registry)

    assert report["status"] == "PRODUCT_QA_GATE_CRITICAL"
    assert report["products_count"] == 2
    assert report["passed_count"] == 1
    assert report["critical_count"] == 1
    assert report["gates"]["read_only"] is True
    assert report["gates"]["product_execution_allowed"] is False
    assert report["gates"]["auto_fix_allowed"] is False
    assert report["gates"]["deploy_allowed"] is False
    assert report["real_action_executed"] is False
    assert report["paid_ai_call_executed"] is False
    assert report["instagram_publish_executed"] is False