from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase70a_safe_patch_proposer.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase70a_safe_patch", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase70a_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_safe_patch_proposer_policy.json").exists()
    assert (ROOT / "docs" / "KOS_SAFE_PATCH_PROPOSER_V070A.md").exists()


def test_phase70a_proposes_without_applying():
    mod = load_module()
    result = mod.build_patch_proposal(
        objective="melhorar documentacao operacional",
        files=["README.md"],
        proposal_id="TEST-70A-SAFE",
    )

    assert result["status"] == "KOS_SAFE_PATCH_PROPOSAL_READY"
    assert result["target_file_modified"] is False
    assert result["patch_applied"] is False
    assert result["operator_review_required"] is True
    assert result["apply_requires_future_gate"] is True
    assert result["auto_execution_enabled"] is False


def test_phase70a_blocks_secret_paths():
    mod = load_module()
    result = mod.build_patch_proposal(
        objective="ler segredo",
        files=["local_runtime/kos_secrets/meta_access_token.txt"],
        proposal_id="TEST-70A-BLOCK",
    )

    assert result["status"] == "KOS_SAFE_PATCH_PROPOSAL_BLOCKED"
    assert result["target_file_modified"] is False
    assert result["patch_applied"] is False


def test_phase70a_blocks_real_publish_terms():
    mod = load_module()
    result = mod.build_patch_proposal(
        objective="usar --execute-real-publish agora",
        files=["README.md"],
        proposal_id="TEST-70A-PUBLISH-BLOCK",
    )

    assert result["status"] == "KOS_SAFE_PATCH_PROPOSAL_BLOCKED"
    assert result["target_file_modified"] is False
    assert result["patch_applied"] is False
