# -*- coding: utf-8 -*-
"""
Smoke test do AutoReporter.

Valida:
- criacao de relatorio
- existencia do arquivo
- conteudo minimo obrigatorio

Uso:
python smoke_test_auto_reporter.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from agents.auto_reporter import AutoReporter


REQUIRED_TEXT = [
    "## 1. Objetivo do módulo",
    "## 2. Arquivos criados/alterados",
    "## 3. Fluxo operacional",
    "## 4. Pontos fortes",
    "## 5. Gargalos",
    "## 6. Riscos futuros",
    "## 7. Próximo passo correto",
    "## 8. Próximo passo que NÃO deve ser feito agora",
    "## 9. Impacto no K-Atlas OS",
    "## 10. Score do módulo",
    "## 11. Decisão do professor",
]


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "module_reports"
        reporter = AutoReporter(output_dir=output_dir)

        result = reporter.generate_report_from_payload(
            {
                "module_name": "Smoke Test Module",
                "objective": "Validar geracao de relatorio operacional padronizado.",
                "files_changed": [
                    "agents/auto_reporter.py",
                    "smoke_test_auto_reporter.py",
                ],
                "operational_flow": "Entrada por payload ou CLI, renderizacao Markdown e persistencia em disco.",
                "strengths": [
                    "Formato padronizado",
                    "Persistencia Markdown",
                    "Validacao minima obrigatoria",
                ],
                "bottlenecks": [
                    "Ainda nao integrado ao kernel",
                    "Ainda nao usa memoria operacional",
                ],
                "future_risks": [
                    "Relatorios podem ficar superficiais se payload for pobre",
                    "Sem revisao humana ainda",
                ],
                "next_step": "Integrar ao kernel, CLI e cockpit.",
                "not_now": "Nao gerar relatorios autonomos sem aprovacao.",
                "impact": "Cria base de auditoria e governanca para evolucao modular.",
                "professor_decision": "aprovado com ressalvas",
                "decision_reason": "Funcional para governanca inicial, mas ainda precisa de integracao com memoria e approvals.",
                "tags": ["smoke_test", "reports"],
                "scores": {
                    "arquitetura": 8.0,
                    "modularidade": 8.0,
                    "estabilidade": 8.0,
                    "escalabilidade": 7.0,
                    "clareza": 9.0,
                    "risco_operacional": 7.0,
                    "preparacao_futura": 8.5,
                    "maturidade_do_nucleo": 7.5,
                },
            }
        )

        assert_true(result["success"], "geracao do relatorio falhou")

        report_path = Path(result["report_path"])
        metadata_path = Path(result["metadata_path"])

        assert_true(report_path.exists(), "arquivo Markdown nao foi criado")
        assert_true(metadata_path.exists(), "arquivo JSON de metadados nao foi criado")

        content = report_path.read_text(encoding="utf-8")

        for marker in REQUIRED_TEXT:
            assert_true(marker in content, "marcador obrigatorio ausente: " + marker)

        validation = reporter.validate_markdown(content)
        assert_true(validation["success"], "validacao do markdown falhou")

        listed = reporter.list_reports({"limit": 10})
        assert_true(listed["success"], "listagem de relatorios falhou")
        assert_true(listed["total"] >= 1, "nenhum relatorio listado")

        print("AutoReporter smoke test OK")
        print("report_path:", report_path)
        print("metadata_path:", metadata_path)
