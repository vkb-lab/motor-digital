from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import json
from pathlib import Path


@dataclass
class PlannedStep:
    title: str
    description: str
    action: str
    risk_level: int = 0
    requires_approval: bool = False
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPlan:
    original_command: str
    intent: str
    summary: str
    steps: List[PlannedStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "planned"

    def to_markdown(self) -> str:
        lines = []
        lines.append(f"# Plano do K-Atlas")
        lines.append("")
        lines.append(f"**Pedido original:** {self.original_command}")
        lines.append(f"**Intenção:** {self.intent}")
        lines.append(f"**Resumo:** {self.summary}")
        lines.append("")
        lines.append("## Etapas")
        for i, step in enumerate(self.steps, 1):
            approval = "SIM" if step.requires_approval else "NÃO"
            lines.append(f"### {i}. {step.title}")
            lines.append(f"- Descrição: {step.description}")
            lines.append(f"- Ação: `{step.action}`")
            lines.append(f"- Risco: {step.risk_level}")
            lines.append(f"- Exige confirmação: {approval}")
            lines.append("")
        return "\n".join(lines)

    def to_dict(self):
        return {
            "original_command": self.original_command,
            "intent": self.intent,
            "summary": self.summary,
            "created_at": self.created_at,
            "status": self.status,
            "steps": [
                {
                    "title": s.title,
                    "description": s.description,
                    "action": s.action,
                    "risk_level": s.risk_level,
                    "requires_approval": s.requires_approval,
                    "payload": s.payload,
                }
                for s in self.steps
            ],
        }


def build_plan(command: str) -> AgentPlan:
    text = (command or "").strip()
    low = text.lower()

    if any(x in low for x in ["use ia", "com ia", "ai brain", "inteligência artificial", "inteligencia artificial"]):
        return AgentPlan(
            original_command=text,
            intent="ai_brain_task",
            summary="Usar o AI Brain com Gemini para gerar análise, estratégia, copy, código ou plano técnico.",
            steps=[
                PlannedStep(
                    title="Consultar AI Brain",
                    description="Enviar o pedido para o Gemini com contexto do K-Atlas.",
                    action="ask_ai_brain",
                    risk_level=0,
                    requires_approval=False
                ),
                PlannedStep(
                    title="Salvar resposta da IA",
                    description="Registrar o relatório em k_atlas/reports.",
                    action="save_plan",
                    risk_level=0,
                    requires_approval=False
                )
            ]
        )

    if any(x in low for x in ["crie uma landing", "landing page", "site", "página", "pagina"]):
        return AgentPlan(
            original_command=text,
            intent="build_landing_page",
            summary="Criar estrutura inicial de uma landing page com arquivos, briefing e próximos passos.",
            steps=[
                PlannedStep(
                    title="Criar pasta do projeto",
                    description="Criar uma pasta organizada dentro do workspace do K-Atlas.",
                    action="create_project_folder",
                    risk_level=1,
                    requires_approval=False,
                    payload={"project_type": "landing_page"}
                ),
                PlannedStep(
                    title="Gerar briefing técnico",
                    description="Criar README com objetivo, público, estrutura e páginas.",
                    action="create_project_readme",
                    risk_level=1,
                    requires_approval=False
                ),
                PlannedStep(
                    title="Gerar arquivos base",
                    description="Criar arquivos HTML/CSS/JS iniciais ou plano Next.js conforme decisão.",
                    action="create_basic_web_files",
                    risk_level=2,
                    requires_approval=True
                ),
                PlannedStep(
                    title="Salvar plano de execução",
                    description="Registrar o plano em k_atlas/plans.",
                    action="save_plan",
                    risk_level=0,
                    requires_approval=False
                ),
            ]
        )

    if any(x in low for x in ["crie um app", "criar app", "aplicativo", "sistema", "saas"]):
        return AgentPlan(
            original_command=text,
            intent="build_app",
            summary="Transformar a ideia em plano de aplicativo e preparar estrutura inicial.",
            steps=[
                PlannedStep("Definir escopo", "Gerar escopo funcional do app.", "create_app_scope", 0, False),
                PlannedStep("Criar projeto", "Criar pasta do projeto no workspace.", "create_project_folder", 1, False, {"project_type": "app"}),
                PlannedStep("Gerar arquitetura", "Criar documentação com stack, páginas, banco e APIs.", "create_architecture_doc", 1, False),
                PlannedStep("Criar arquivos iniciais", "Criar estrutura inicial de código.", "create_app_files", 2, True),
            ]
        )

    if any(x in low for x in ["analise minha área de trabalho", "analise minha area de trabalho", "desktop"]):
        return AgentPlan(
            original_command=text,
            intent="analyze_desktop",
            summary="Mapear a Área de Trabalho e gerar relatório sem mover nada.",
            steps=[
                PlannedStep("Mapear Desktop", "Listar arquivos e pastas.", "scan_desktop", 0, False),
                PlannedStep("Gerar relatório", "Salvar relatório em k_atlas/reports.", "create_desktop_report", 0, False),
                PlannedStep("Sugerir organização", "Criar plano de organização sem mover arquivos.", "suggest_desktop_organization", 0, False),
            ]
        )

    if any(x in low for x in ["email", "gmail", "e-mail"]):
        return AgentPlan(
            original_command=text,
            intent="gmail_work",
            summary="Trabalhar com Gmail respeitando limites de permissão.",
            steps=[
                PlannedStep("Abrir Gmail", "Abrir Gmail no navegador.", "open_url", 1, False, {"url": "https://mail.google.com"}),
                PlannedStep("Explicar limite", "Informar que ler emails exige Gmail API/OAuth.", "explain_gmail_api_needed", 0, False),
                PlannedStep("Preparar integração", "Criar plano para conectar Gmail API futuramente.", "create_gmail_integration_plan", 1, False),
            ]
        )

    if any(x in low for x in ["instagram", "insta"]):
        return AgentPlan(
            original_command=text,
            intent="instagram_work",
            summary="Trabalhar com Instagram sem publicar automaticamente sem autorização.",
            steps=[
                PlannedStep("Abrir Instagram", "Abrir Instagram no navegador.", "open_url", 1, False, {"url": "https://www.instagram.com"}),
                PlannedStep("Criar plano social", "Se o pedido envolver conteúdo, criar plano de campanha.", "create_social_plan", 1, False),
                PlannedStep("Avisar limite", "Publicação automática exige Meta Graph API e confirmação.", "explain_instagram_api_needed", 0, False),
            ]
        )

    return AgentPlan(
        original_command=text,
        intent="general_digital_task",
        summary="Pedido geral recebido. O agente irá planejar antes de executar.",
        steps=[
            PlannedStep("Interpretar pedido", "Entender objetivo principal.", "interpret", 0, False),
            PlannedStep("Criar plano", "Gerar etapas executáveis.", "save_plan", 0, False),
            PlannedStep("Pedir confirmação", "Antes de ações sensíveis, pedir confirmação.", "approval_required", 0, False),
        ]
    )


def save_plan(plan: AgentPlan) -> Path:
    plans_dir = Path.cwd() / "k_atlas" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = plans_dir / f"plan_{stamp}.md"
    json_path = plans_dir / f"plan_{stamp}.json"

    md_path.write_text(plan.to_markdown(), encoding="utf-8")
    json_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    return md_path

