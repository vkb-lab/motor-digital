# -*- coding: utf-8 -*-
"""
Smoke test do LearningAgent.

Uso:
python smoke_test_learning_agent.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from agents.learning_agent import LearningAgent
from core.kernel import create_kernel


ROOT = Path(__file__).resolve().parent


def assert_success(result, label: str) -> None:
    if not result.success:
        print(label)
        print(result.to_dict())
        raise SystemExit(1)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)

        kernel = create_kernel(root_path=ROOT)
        kernel.start(load_state=True)

        learning_agent = LearningAgent(root_path=temp_root)
        kernel.register_agent(learning_agent, replace=True, roles=["system"])

        ping = kernel.execute("learning_agent.ping")
        assert_success(ping, "ping failed")

        lesson = kernel.execute(
            "learning_agent.learn",
            payload={
                "title": "Smoke tests devem usar memoria temporaria",
                "content": "Testes automatizados nao devem alterar arquivos operacionais reais.",
                "type": "best_practice",
                "tags": ["tests", "memory", "quality"],
                "source": "smoke_test",
                "importance": 3,
                "related_agents": ["task_agent", "memory_agent"],
            },
        )
        assert_success(lesson, "learn failed")

        error = kernel.execute(
            "learning_agent.error",
            payload={
                "title": "Memoria operacional alterada por teste",
                "symptom": "Arquivo memory/tasks.json ficou modificado apos smoke test.",
                "cause": "Teste gravava diretamente na memoria operacional.",
                "fix": "Usar TemporaryDirectory e storage_path temporario.",
                "prevention": "Todo smoke test com escrita deve usar armazenamento isolado.",
                "severity": "medium",
                "tags": ["tests", "memory", "regression"],
                "source": "smoke_test",
                "related_agents": ["task_agent"],
            },
        )
        assert_success(error, "error failed")

        playbook = kernel.execute(
            "learning_agent.playbook",
            payload={
                "title": "Criar agente K-Atlas com seguranca",
                "objective": "Padronizar criacao de agentes com teste e persistencia segura.",
                "context": "Todo novo agente precisa ser modular, testavel e auditavel.",
                "steps": [
                    "Criar arquivo em agents/",
                    "Herdar de BaseAgent",
                    "Criar smoke test isolado",
                    "Executar dev_runner",
                    "Integrar no boot apenas apos validacao",
                    "Commitar checkpoint"
                ],
                "expected_result": "Agente criado, testado e pronto para integracao.",
                "failure_modes": [
                    "Teste altera memoria real",
                    "Permissao nao registrada",
                    "Agente nao registrado no kernel"
                ],
                "tags": ["agents", "kernel", "quality"],
                "source": "smoke_test",
            },
        )
        assert_success(playbook, "playbook failed")

        memory_to_playbook = kernel.execute(
            "learning_agent.memory_to_playbook",
            payload={
                "title": "Converter decisao em procedimento",
                "memory_content": "Quando uma decisao operacional se repetir, ela deve virar playbook reutilizavel.",
                "objective": "Criar procedimento a partir de memoria institucional.",
                "tags": ["memory", "playbook"],
                "source": "smoke_test",
            },
        )
        assert_success(memory_to_playbook, "memory_to_playbook failed")

        training = kernel.execute(
            "learning_agent.training",
            payload={
                "title": "Regra de treinamento para agentes futuros",
                "content": "Antes de automatizar uma acao, validar se existe playbook e permissao explicita.",
                "type": "rule",
                "tags": ["training", "agents", "governance"],
                "source": "smoke_test",
                "target_agents": ["future_agents", "robots"],
                "importance": 3,
            },
        )
        assert_success(training, "training failed")

        search = kernel.execute(
            "learning_agent.search",
            payload={
                "query": "playbook",
                "limit": 10,
            },
        )
        assert_success(search, "search failed")

        stats = kernel.execute("learning_agent.stats")
        assert_success(stats, "stats failed")

        export_pack = kernel.execute("learning_agent.export_training_pack")
        assert_success(export_pack, "export_training_pack failed")

        print("LearningAgent smoke test OK")
        print("stats:", stats.output["totals"])
        print("training_pack:", export_pack.output["output_path"])

        kernel.stop(save_state=True)
