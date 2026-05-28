
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from k_atlas.self_evolution.approval_gate import approve_patch, reject_patch, require_human_approval
from k_atlas.self_evolution.ask_engineer import create_patch_request, list_patch_requests
from k_atlas.self_evolution.patch_engine import create_patch_proposal, list_patch_inbox
from k_atlas.self_evolution.risk_analyzer import analyze_risk


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        target_dir = root / "sample"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / "module.py"
        original_content = "VALUE = 1\n"
        proposed_content = "VALUE = 2\n"
        target_file.write_text(original_content, encoding="utf-8")

        request_result = create_patch_request(
            title="Melhorar modulo de exemplo",
            objective="Criar pedido supervisionado de melhoria.",
            context="Teste de autoevolucao supervisionada.",
            source="smoke_test",
            priority="normal",
            tags=["self_evolution", "smoke_test"],
            related_files=["sample/module.py"],
            root_path=root,
        )

        assert_true(request_result["success"], "pedido de melhoria falhou")
        assert_true(Path(request_result["path"]).exists(), "arquivo de pedido nao criado")
        assert_true(list_patch_requests(root_path=root)["total"] == 1, "pedido nao listado")

        patch_result = create_patch_proposal(
            title="Patch supervisionado de exemplo",
            objective="Propor alteracao sem aplicar automaticamente.",
            target_file="sample/module.py",
            proposed_content=proposed_content,
            request_id=request_result["request"]["request_id"],
            author="smoke_test",
            root_path=root,
            tags=["self_evolution", "patch"],
        )

        assert_true(patch_result["success"], "proposta de patch falhou")
        assert_true(Path(patch_result["patch_path"]).exists(), "arquivo de patch nao criado")
        assert_true(Path(patch_result["diff_path"]).exists(), "arquivo diff nao criado")
        assert_true(Path(patch_result["rollback_path"]).exists(), "rollback nao criado")
        assert_true(Path(patch_result["snapshot"]["snapshot_path"]).exists(), "snapshot nao criado")
        assert_true(patch_result["can_auto_apply"] is False, "auto apply nao deveria estar habilitado")
        assert_true(target_file.read_text(encoding="utf-8") == original_content, "arquivo alvo foi alterado automaticamente")
        assert_true(list_patch_inbox(root_path=root)["total"] == 1, "patch nao listado no inbox")

        patch_data = json.loads(Path(patch_result["patch_path"]).read_text(encoding="utf-8"))
        approval_required = require_human_approval(patch_data)

        assert_true(approval_required["requires_human_approval"] is True, "approval humano deveria ser obrigatorio")
        assert_true(approval_required["can_auto_apply"] is False, "auto apply deveria continuar bloqueado")

        approval = approve_patch(
            patch_path=patch_result["patch_path"],
            approved_by="professor",
            reason="Aprovado apenas para validar fluxo supervisionado.",
            root_path=root,
        )
        assert_true(approval["success"], "approval falhou")
        assert_true(approval["can_auto_apply"] is False, "approval nao deve liberar auto apply")
        assert_true(Path(approval["approved_path"]).exists(), "patch aprovado nao foi salvo")

        rejection = reject_patch(
            patch_path=patch_result["patch_path"],
            rejected_by="professor",
            reason="Rejeicao de teste para validar fluxo.",
            root_path=root,
        )
        assert_true(rejection["success"], "rejection falhou")
        assert_true(Path(rejection["rejected_path"]).exists(), "patch rejeitado nao foi salvo")

        high_risk = analyze_risk(
            target_files=["core/kernel.py"],
            proposed_content="import subprocess\nsubprocess.run(['danger'])\n",
            patch_text="delete core",
        )

        assert_true(high_risk["risk_level"] in ["blocked", "high"], "risco alto nao detectado")
        assert_true(high_risk["requires_human_approval"] is True, "approval humano deveria ser exigido")
        assert_true(target_file.read_text(encoding="utf-8") == original_content, "arquivo alvo foi alterado no final do teste")

        print("Self Evolution smoke test OK")
        print("request_path:", request_result["path"])
        print("patch_path:", patch_result["patch_path"])
        print("risk:", patch_result["risk"])
        print("approved_path:", approval["approved_path"])
        print("rejected_path:", rejection["rejected_path"])
