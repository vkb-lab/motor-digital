from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_weekly_ops"
LATEST = OUT_DIR / "latest_weekly_operator_workspace.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_command(label: str, command: str) -> dict[str, str]:
    return {"label": label, "command": command}


def build_week_workspace(week_id: str = "") -> dict[str, Any]:
    if not week_id:
        week_id = "kos-week-" + datetime.now().strftime("%Y%m%d")

    days = [
        {
            "day": 1,
            "theme": "Setup operacional",
            "focus": ["abrir dashboards", "validar Git limpo", "verificar Social Ops", "organizar prioridades"],
            "success": "ambiente aberto, painel funcionando e lista de foco definida",
        },
        {
            "day": 2,
            "theme": "Redes sociais Hupmix",
            "focus": ["gerar estrategia 71B", "validar readiness 71C", "separar imagem HTTPS", "preparar legenda"],
            "success": "estrategia pronta e readiness atualizado sem publicar",
        },
        {
            "day": 3,
            "theme": "Produto SaaS",
            "focus": ["escolher 1 ideia SaaS", "definir usuario alvo", "definir dor", "criar escopo MVP"],
            "success": "1 projeto SaaS definido em formato executavel",
        },
        {
            "day": 4,
            "theme": "Landing e oferta",
            "focus": ["criar promessa", "criar headline", "definir CTA", "preparar copy inicial"],
            "success": "landing/copy inicial pronta para virar produto",
        },
        {
            "day": 5,
            "theme": "Administração",
            "focus": ["organizar tarefas pendentes", "listar contas/acessos", "separar pendencias financeiras", "definir agenda"],
            "success": "admin operacional limpo e proxima semana previsivel",
        },
        {
            "day": 6,
            "theme": "Teste controlado de publicação",
            "focus": ["usar somente Hupmix", "validar imagem publica HTTPS", "validar legenda", "rodar readiness", "nao publicar sem gate"],
            "success": "publicacao pronta para decisao humana, sem executar automaticamente",
        },
        {
            "day": 7,
            "theme": "Revisão e baseline",
            "focus": ["revisar resultados", "registrar aprendizados", "limpar Git", "planejar proxima semana"],
            "success": "semana fechada com memoria operacional",
        },
    ]

    workspace = {
        "status": "KOS_WEEKLY_OPERATOR_WORKSPACE_READY",
        "phase": "72A",
        "week_id": week_id,
        "tracks": {
            "admin": {
                "goal": "reduzir caos operacional e manter rotina minima",
                "daily_action": "registrar pendencias e decidir 1 prioridade real por dia",
            },
            "saas": {
                "goal": "transformar ideias em projetos reaproveitaveis",
                "daily_action": "definir escopo pequeno e evitar expansao precoce",
            },
            "social": {
                "goal": "operar Hupmix com estrategia, auditoria e readiness",
                "daily_action": "gerar ou revisar conteudo sem publicar automaticamente",
            },
        },
        "daily_protocol": [
            "abrir Weekly Operator Workspace",
            "abrir Social Ops Control Center",
            "verificar Git limpo",
            "escolher 1 tarefa principal",
            "executar sem abrir muitas frentes",
            "registrar resultado",
        ],
        "safe_commands": [
            safe_command("Abrir Social Ops", "C:\\Users\\oi\\Desktop\\KOS_Social_Ops_Control_Center.cmd"),
            safe_command("Abrir Weekly Workspace", "C:\\Users\\oi\\Desktop\\KOS_Weekly_Operator_Workspace.cmd"),
            safe_command("Git status", "git --no-pager status --short"),
            safe_command("Gerar estrategia Hupmix", "python scripts\\run_phase71b_social_strategy_generator.py --target hupmix --objective \"estrategia semanal Hupmix\" --campaign hupmix-weekly"),
            safe_command("Readiness Hupmix sem publicar", "python scripts\\run_phase71c_social_publish_readiness_auditor.py --target hupmix --asset-url https://example.com/imagem.png --caption \"legenda de teste sem publicar\""),
            safe_command("Status ponte ChatGPT", "powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action status"),
        ],
        "guardrails": {
            "auto_publish_enabled": False,
            "auto_execution_enabled": False,
            "operator_review_required": True,
            "parada_atlantida_locked": True,
            "target_test_account": "hupmix",
            "paid_ai_locked": True,
            "browser_scraping_enabled": False,
            "browser_logged_account_automation_used": False,
            "instagram_publish_executed": False,
            "real_action_executed": False,
        },
        "days": days,
        "created_at": now_iso(),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{week_id}.json"
    path.write_text(json.dumps(workspace, indent=2, ensure_ascii=False), encoding="utf-8")
    LATEST.write_text(json.dumps(workspace, indent=2, ensure_ascii=False), encoding="utf-8")

    workspace["path"] = str(path)
    return workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week-id", default="")
    args = parser.parse_args()

    result = build_week_workspace(week_id=args.week_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
