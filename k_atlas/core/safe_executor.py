from pathlib import Path
from datetime import datetime

from k_atlas.core.task_planner import build_plan, save_plan
from k_atlas.core.approval_gate import create_approval_request, approval_message
from k_atlas.core.desktop_actions import open_url, create_desktop_report, suggest_desktop_organization
from k_atlas.core.project_builder import create_project_folder, create_basic_web_files, create_architecture_doc
from k_atlas.core.ai_brain import think


def execute_plan(command: str, auto_confirm: bool = False):
    plan = build_plan(command)
    plan_file = save_plan(plan)

    results = []
    results.append(f"Plano criado: {plan_file}")

    current_project_path = None

    for step in plan.steps:
        if step.requires_approval and not auto_confirm:
            approval_file = create_approval_request(plan, step)
            results.append(approval_message(step, approval_file))
            continue

        if step.action == "ask_ai_brain":
            answer, report, model_name = think(command)
            results.append(f"AI Brain respondeu usando {model_name}.")
            results.append(f"Relatório IA salvo em: {report}")

        elif step.action == "open_url":
            url = step.payload.get("url")
            if url:
                results.append(open_url(url))

        elif step.action == "create_project_folder":
            project_type = step.payload.get("project_type", "project")
            current_project_path = create_project_folder(command, project_type)
            results.append(f"Pasta de projeto criada: {current_project_path}")

        elif step.action == "create_project_readme":
            results.append("README inicial criado junto com a pasta do projeto.")

        elif step.action == "create_basic_web_files":
            if current_project_path:
                files = create_basic_web_files(current_project_path)
                results.append("Arquivos web criados: " + ", ".join(str(f.name) for f in files))
            else:
                results.append("Arquivos web aguardando pasta de projeto.")

        elif step.action == "create_app_scope":
            results.append("Escopo inicial do app registrado no plano.")

        elif step.action == "create_architecture_doc":
            if current_project_path:
                doc = create_architecture_doc(current_project_path, command)
                results.append(f"Documento de arquitetura criado: {doc}")
            else:
                current_project_path = create_project_folder(command, "app")
                doc = create_architecture_doc(current_project_path, command)
                results.append(f"Projeto e arquitetura criados: {doc}")

        elif step.action == "create_app_files":
            results.append("Criação de arquivos de app exige confirmação.")

        elif step.action == "scan_desktop":
            results.append("Área de Trabalho analisada.")

        elif step.action == "create_desktop_report":
            results.append(create_desktop_report())

        elif step.action == "suggest_desktop_organization":
            results.append(suggest_desktop_organization())

        elif step.action == "explain_gmail_api_needed":
            results.append("Para ler emails, será necessário conectar Gmail API/OAuth. Por segurança, não vou fingir que li mensagens.")

        elif step.action == "create_gmail_integration_plan":
            path = Path.cwd() / "k_atlas" / "plans" / "gmail_api_integration_plan.md"
            path.write_text("""# Plano de integração Gmail API

## Objetivo
Permitir que o K-Atlas leia emails com autorização do usuário.

## Etapas
1. Criar projeto Google Cloud
2. Ativar Gmail API
3. Configurar OAuth
4. Salvar token com segurança
5. Buscar emails por data
6. Resumir remetente, assunto e conteúdo
7. Nunca enviar email sem confirmação
""", encoding="utf-8")
            results.append(f"Plano Gmail API criado: {path}")

        elif step.action == "create_social_plan":
            path = Path.cwd() / "k_atlas" / "plans" / f"social_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            path.write_text(f"# Plano Social\n\nPedido: {command}\n\nStatus: rascunho.", encoding="utf-8")
            results.append(f"Plano social criado: {path}")

        elif step.action == "explain_instagram_api_needed":
            results.append("Publicação automática no Instagram exige Meta Graph API, conta profissional e confirmação.")

        elif step.action == "save_plan":
            results.append("Plano salvo para continuidade.")

        else:
            results.append(f"Etapa registrada: {step.title}")

    return plan, results

