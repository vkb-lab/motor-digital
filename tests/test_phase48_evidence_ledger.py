from k_atlas.kaizen.evidence_ledger import build_evidence_entry, append_evidence, summarize_evidence

def test_build_evidence_entry_is_safe():
    entry = build_evidence_entry(source="test", note="safe test")

    assert entry["status"] == "KOS_AUTONOMY_EVIDENCE_RECORDED"
    assert entry["real_action_executed"] is False
    assert entry["paid_ai_call_executed"] is False
    assert entry["instagram_publish_executed"] is False
    assert entry["external_side_effects_executed"] is False

def test_append_evidence_and_summary_are_safe():
    entry = append_evidence(source="test_phase48", note="test append")
    summary = summarize_evidence(limit=5)

    assert entry["evidence_id"]
    assert summary["status"] == "KOS_EVIDENCE_LEDGER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
    assert summary["external_side_effects_executed"] is False
