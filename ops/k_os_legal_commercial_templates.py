# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "legal" / "k_os_legal_commercial_license_policy.json"
REPORT_DIR = ROOT / "reports" / "legal"
TEMPLATE_DIR = REPORT_DIR / "templates"
MEMORY_DIR = ROOT / "memory" / "legal"
LATEST_JSON = REPORT_DIR / "latest_legal_commercial_templates_report.json"
LATEST_MD = REPORT_DIR / "latest_legal_commercial_templates_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

PREREQUISITES = [
    "reports/security/k_os_015_closure_report.json",
    "reports/schema/k_os_016_closure_report.json",
    "reports/governance/k_os_017_closure_report.json",
    "reports/vault/k_os_018_closure_report.json",
    "reports/audit/k_os_019_closure_report.json",
    "reports/mission_control/k_os_020_closure_report.json",
    "reports/risk/k_os_021_closure_report.json",
    "reports/external_sandbox/k_os_022_closure_report.json",
    "reports/enterprise/k_os_023_closure_report.json",
    "reports/incident/k_os_024_closure_report.json"
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc)}


def load_policy() -> dict[str, Any]:
    data = read_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Politica legal comercial nao encontrada.")
    return data


def prerequisite_status() -> list[dict[str, Any]]:
    items = []
    for rel in PREREQUISITES:
        path = ROOT / rel
        data = read_json(path)
        items.append({
            "path": rel,
            "exists": path.exists(),
            "ok": bool(data and data.get("ok") is True),
            "status": data.get("status") if isinstance(data, dict) else "missing"
        })
    return items


def templates() -> dict[str, str]:
    header = (
        "AVISO OPERACIONAL\n\n"
        "Este documento e um template operacional do K-OS. "
        "Nao e aconselhamento juridico. "
        "Uso comercial real exige revisao juridica, revisao comercial e assinatura formal das partes.\n\n"
    )

    return {
        "agent_subscription_terms_template.md": header + """# Termos de Assinatura de Agente IA

## 1. Partes

Contratante: [NOME LEGAL DO CLIENTE]  
Fornecedor: [NOME LEGAL DO FORNECEDOR]  
Projeto: [NOME DO PROJETO]  
Agente: [AGENT_ID]  
Plano: [PLANO]  
Ciclo de cobranca: [MENSAL/ANUAL/ENTERPRISE]  

## 2. Objeto

O fornecedor disponibiliza ao contratante acesso controlado ao agente IA indicado no pedido comercial.

O agente pode executar apenas as capacidades permitidas no pedido comercial e no License Gate do K-OS.

## 3. Ativacao

A ativacao depende de:

- pedido comercial aprovado
- assinatura ou aceite formal
- licenca ativa
- permissao K-OS
- escopo definido
- approval gate quando aplicavel
- revisao juridica antes de uso real

## 4. Limites de uso

O cliente nao pode usar o agente para:

- finalidade ilegal
- abuso, fraude ou spam
- coleta indevida de dados
- tentativa de burlar gates
- publicacao externa sem aprovacao
- envio externo sem aprovacao
- engenharia reversa do sistema

## 5. Suspensao segura

O fornecedor pode suspender ou revogar acesso em caso de:

- falta de pagamento
- ausencia de acordo vigente
- risco de seguranca
- uso indevido
- disputa contratual
- ordem legal
- incidente operacional

Suspensao segura significa desativar agente, revogar licenca, bloquear conectores, congelar execucao e preservar auditoria.

## 6. Dados e auditoria

Logs de auditoria devem ser preservados.  
Exclusao de dados de cliente exige politica formal, base contratual e revisao juridica.

## 7. Sem garantia de resultado

O agente IA apoia operacoes. Ele nao garante receita, resultado comercial, decisao automatica perfeita ou ausencia total de erro.

## 8. Revisao obrigatoria

Este template so pode ser usado comercialmente apos revisao juridica.
""",

        "agent_license_agreement_template.md": header + """# Contrato de Licenca de Agente IA

## 1. Licenca

O fornecedor concede ao cliente uma licenca limitada, revogavel, nao exclusiva e nao transferivel para uso do agente IA [AGENT_ID].

## 2. Escopo

A licenca permite apenas:

- [CAPACIDADE_1]
- [CAPACIDADE_2]
- [CAPACIDADE_3]

Conectores permitidos:

- [CONECTOR_1]
- [CONECTOR_2]

Tudo que nao estiver explicitamente permitido esta bloqueado por padrao.

## 3. Controle K-OS

A operacao do agente depende de:

- License Gate
- AI Risk Classifier
- Agent Permission Matrix
- Vault Guard quando houver credenciais
- External API Sandbox quando houver integracao externa
- Human Approval quando houver risco medio, alto ou critico

## 4. Revogacao

A licenca pode ser revogada ou suspensa conforme termos comerciais.

A revogacao nao autoriza apagamento silencioso de dados de cliente nem exclusao de logs de auditoria.

## 5. Emergencia

Em emergencia, o fornecedor pode acionar lockdown seguro:

- desativar agente
- suspender licenca
- bloquear conectores
- congelar tarefas
- bloquear novos outputs
- preservar auditoria
- gerar relatorio de incidente

## 6. Propriedade intelectual

O K-OS, seus agentes, fluxos, codigo, templates e arquitetura continuam pertencendo ao fornecedor, salvo previsao expressa em contrato assinado.

## 7. Revisao obrigatoria

Este documento precisa ser revisado por advogado antes de uso externo.
""",

        "commercial_order_form_template.md": header + """# Pedido Comercial de Agente IA

## Cliente

Nome legal: [NOME LEGAL]  
Alias operacional: [ALIAS]  
Contato aprovador: [NOME/EMAIL]  
Contato financeiro: [NOME/EMAIL]  
Contato emergencial: [NOME/EMAIL]  

## Agente

Agent ID: [AGENT_ID]  
Nome comercial: [NOME DO AGENTE]  
Plano: [TRIAL/MENSAL/ANUAL/ENTERPRISE]  
Inicio: [DATA]  
Fim/Renovacao: [DATA]  

## Capacidades permitidas

- [CAPACIDADE_1]
- [CAPACIDADE_2]
- [CAPACIDADE_3]

## Conectores permitidos

- [CONECTOR_1]
- [CONECTOR_2]

Se nenhum conector externo estiver aprovado, todos permanecem bloqueados.

## Valores

Setup: [VALOR]  
Mensalidade: [VALOR]  
Uso adicional: [REGRA]  
Impostos: [REGRA]  

## Gates obrigatorios

- License Gate
- Risk Classifier
- Human Approval
- Incident Runbook
- External API Sandbox para qualquer conector externo

## Aceite

Cliente: __________________________ Data: __________  
Fornecedor: _______________________ Data: __________  
Revisao juridica: _________________ Data: __________  
""",

        "acceptable_use_policy_template.md": header + """# Politica de Uso Aceitavel

## Permitido

- uso dentro do escopo contratado
- automacoes locais aprovadas
- geracao de conteudo revisavel
- apoio a campanhas e operacoes
- uso com approval gate quando necessario

## Proibido

- spam
- fraude
- uso ilegal
- tentativa de burlar limites
- publicacao externa sem aprovacao
- envio externo sem aprovacao
- exposicao de chaves ou credenciais
- upload de dados sensiveis sem revisao
- tentativa de remover auditoria
- uso para causar dano a terceiros

## Violacao

Violacoes podem gerar:

- suspensao
- revogacao de licenca
- lockdown seguro
- investigacao
- relatorio de incidente
- encerramento contratual conforme documento assinado

## Regra de seguranca

Nenhuma acao emergencial pode apagar logs de auditoria.
""",

        "sla_support_terms_template.md": header + """# SLA e Suporte Basico

## Canais

Canal principal: [CANAL]  
Horario de atendimento: [HORARIO]  
Contato emergencial: [CONTATO]  

## Severidade

SEV1 Critical: risco de dados, chaves, cliente, legal, reputacao ou operacao.  
SEV2 High: falha relevante de agente, deploy, licenca ou integracao.  
SEV3 Medium: falha controlada sem exposicao externa.  
SEV4 Low: ajuste local ou melhoria.

## Resposta

SEV1: resposta imediata conforme disponibilidade contratada.  
SEV2: resposta no mesmo dia util ou conforme plano.  
SEV3: resposta planejada.  
SEV4: backlog.

## Limites

SLA nao garante resultado comercial, receita, conversao, disponibilidade de terceiros ou ausencia total de falhas de IA.

## Incidentes

Incidentes seguem o K-OS Incident Response and Rollback Runbook.
""",

        "data_processing_addendum_outline.md": header + """# Anexo de Tratamento de Dados - Estrutura

## Objetivo

Definir responsabilidades sobre dados pessoais quando o agente IA processar dados de cliente ou usuarios.

## Papeis

Controlador: [DEFINIR]  
Operador: [DEFINIR]  
Suboperadores: [DEFINIR SE EXISTIREM]  

## Categorias de dados

- [CATEGORIA_1]
- [CATEGORIA_2]
- [CATEGORIA_3]

## Finalidade

- [FINALIDADE_1]
- [FINALIDADE_2]

## Medidas operacionais

- acesso minimo necessario
- logs de auditoria
- approval gate
- vault para credenciais
- sandbox para conectores externos
- incidente com runbook

## Incidente

Qualquer incidente deve ser avaliado, registrado e tratado conforme politica de incidente vigente.

## Revisao obrigatoria

Este anexo precisa de revisao juridica e de privacidade antes de uso externo.
""",

        "emergency_suspension_revocation_policy.md": header + """# Politica de Suspensao, Revogacao e Lockdown Seguro

## Gatilhos

- falta de pagamento
- fim de contrato
- ausencia de acordo vigente
- violacao de uso aceitavel
- risco de seguranca
- incidente operacional
- disputa juridica ou comercial
- ordem legal ou regulatoria

## Acoes permitidas

- suspender licenca
- revogar licenca
- desativar agente
- bloquear conectores externos
- congelar execucao
- bloquear novos outputs
- preservar auditoria
- gerar relatorio de incidente

## Acoes proibidas

- apagar dados de cliente silenciosamente
- apagar logs de auditoria
- destruir ativos do cliente
- executar punicao tecnica fora do contrato
- enviar mensagem externa sem approval gate
- publicar conteudo externo sem approval gate

## Reativacao

Reativacao exige:

- motivo resolvido
- aprovacao humana
- revisao do License Gate
- verificacao de risco
- registro de auditoria
""",

        "commercial_readiness_checklist.md": header + """# Checklist Comercial para Venda de Agente IA

## Antes de vender

- agente possui ID definido
- escopo documentado
- capacidades permitidas definidas
- conectores externos bloqueados por padrao
- preco definido
- plano definido
- suporte definido
- contato emergencial definido
- revisao juridica planejada

## Antes de ativar

- pedido comercial aprovado
- contrato ou aceite assinado
- licenca ativa
- cliente cadastrado
- License Gate validado
- Risk Classifier validado
- Agent Permission Matrix validada
- Vault Guard validado se houver credenciais
- External API Sandbox validado se houver conectores
- Incident Runbook disponivel

## Durante operacao

- logs preservados
- approval gate usado
- limites respeitados
- incidentes registrados
- mudancas comerciais documentadas

## Antes de revogar

- motivo registrado
- aprovacao humana
- plano de comunicacao
- lockdown seguro
- auditoria preservada
"""
    }


def generate_templates() -> list[dict[str, Any]]:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    result = []
    for filename, content in templates().items():
        path = TEMPLATE_DIR / filename
        path.write_text(content, encoding="utf-8")
        result.append({
            "filename": filename,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "size_bytes": path.stat().st_size
        })
    return result


def build_report() -> dict[str, Any]:
    policy = load_policy()
    prereqs = prerequisite_status()
    template_files = generate_templates()

    prereq_ok = sum(1 for item in prereqs if item["ok"])
    prereq_total = len(prereqs)

    blockers = []

    for item in prereqs:
        if not item["exists"]:
            blockers.append({
                "type": "missing_prerequisite",
                "path": item["path"]
            })
        elif not item["ok"]:
            blockers.append({
                "type": "prerequisite_not_ok",
                "path": item["path"],
                "status": item["status"]
            })

    report = {
        "ok": len(blockers) == 0,
        "checkpoint": "025",
        "module": "k_os_legal_commercial_license_templates",
        "status": "generated",
        "generated_at": now(),
        "templates_generated": len(template_files),
        "template_files": template_files,
        "prerequisites_ok": prereq_ok,
        "prerequisites_total": prereq_total,
        "prerequisites": prereqs,
        "blockers": blockers,
        "legal_status": policy.get("legal_status", {}),
        "commercial_policy": policy.get("commercial_policy", {}),
        "required_gates_before_customer_activation": policy.get("required_gates_before_customer_activation", []),
        "blocked_commercial_claims": policy.get("blocked_commercial_claims", []),
        "safe_claim": "Templates comerciais operacionais criados para venda/assinatura de agentes IA sob permissao K-OS, com revogacao segura e revisao juridica obrigatoria.",
        "restricted_claim": "Nao usar como contrato final sem revisao juridica, revisao comercial e adequacao ao caso concreto.",
        "next_checkpoint": policy.get("next_checkpoint", "026 - K-Billing and Subscription Ledger")
    }

    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Legal Commercial License Templates",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Templates generated: {report.get('templates_generated')}",
        f"- Prerequisites: {report.get('prerequisites_ok')}/{report.get('prerequisites_total')}",
        f"- Generated at: {report.get('generated_at')}",
        "",
        "## Safe Claim",
        "",
        report.get("safe_claim", ""),
        "",
        "## Restricted Claim",
        "",
        report.get("restricted_claim", ""),
        "",
        "## Templates",
        "",
    ]

    for item in report.get("template_files", []):
        lines.append(f"- {item.get('path')}")

    lines.extend([
        "",
        "## Required gates before customer activation",
        "",
    ])

    for gate in report.get("required_gates_before_customer_activation", []):
        lines.append(f"- {gate}")

    lines.extend([
        "",
        "## Blocked commercial claims",
        "",
    ])

    for claim in report.get("blocked_commercial_claims", []):
        lines.append(f"- {claim}")

    lines.extend([
        "",
        "## Blockers",
        "",
    ])

    if report.get("blockers"):
        for blocker in report.get("blockers", []):
            lines.append(f"- {blocker.get('type')}: {blocker.get('path')}")
    else:
        lines.append("- Nenhum blocker operacional encontrado.")

    lines.extend([
        "",
        "## Next checkpoint",
        "",
        f"- {report.get('next_checkpoint')}"
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "legal_commercial_templates.generated",
            "created_at": now(),
            "ok": report.get("ok"),
            "templates_generated": report.get("templates_generated")
        }, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "show"], default="generate")
    args = parser.parse_args()

    if args.mode == "show":
        if LATEST_JSON.exists():
            print(LATEST_JSON.read_text(encoding="utf-8-sig"))
        else:
            print("{}")
        return 0

    report = build_report()
    write_report(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())