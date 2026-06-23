
from pathlib import Path
import argparse
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
KNOWLEDGE = MEMORY / "kos_knowledge"
SKILLS = MEMORY / "kos_skills"
GOV = MEMORY / "kos_governance"
REPORTS = ROOT / "reports"
RUNTIME = ROOT / "local_runtime" / "kos_process_learning_engine"

for p in [KNOWLEDGE, SKILLS, GOV, REPORTS, RUNTIME]:
    p.mkdir(parents=True, exist_ok=True)

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def write_json_if_changed(path: Path, data: dict):
    content = json.dumps(data, ensure_ascii=False, indent=2)
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def write_text_if_changed(path: Path, content: str):
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def build_registry():
    return {
        "status": "KOS_UNIVERSAL_PROCESS_REGISTRY_V1_READY",
        "version": "v1",
        "principle": "Todo caso especifico deve gerar conhecimento reutilizavel.",
        "case_to_pattern_rule": {
            "case_specific": "cliente, produto, marca, ativos, campanha, contexto local",
            "universal_pattern": "processo, fluxo, habilidade, checklist, automacao, criterio de qualidade",
            "runtime": "execucoes, logs, previews e arquivos vivos ficam em local_runtime",
            "git_memory": "codigo, politicas, skills, playbooks e conhecimento promovido ficam no Git"
        },
        "universal_process_layers": [
            {
                "id": "business_context_intake",
                "name": "Captura de contexto do negocio",
                "reusable_for": ["lojas", "saas", "agencias", "clinicas", "multinacionais"],
                "outputs": ["perfil do negocio", "ofertas", "publico", "canais", "restricoes"]
            },
            {
                "id": "positioning_and_social_audit",
                "name": "Auditoria de posicionamento e canais",
                "reusable_for": ["instagram", "site", "whatsapp", "telegram", "landing pages"],
                "outputs": ["diagnostico", "gaps", "oportunidades", "prioridades"]
            },
            {
                "id": "asset_bridge",
                "name": "Ponte de assets reais",
                "reusable_for": ["posts", "videos", "fotos", "catalogos", "depoimentos", "prints"],
                "outputs": ["assets classificados", "fonte", "permissao", "uso operacional"]
            },
            {
                "id": "campaign_factory",
                "name": "Fabrica de campanha",
                "reusable_for": ["conteudo organico", "ads", "promocoes", "lancamentos", "recuperacao comercial"],
                "outputs": ["roteiro", "copy", "briefing", "storyboard", "preview"]
            },
            {
                "id": "character_or_brand_voice_system",
                "name": "Sistema de personagem ou voz de marca",
                "reusable_for": ["mascotes", "especialistas", "vendedores", "porta-vozes", "fundadores"],
                "outputs": ["tom", "falas", "prompts", "guia de consistencia"]
            },
            {
                "id": "local_generation_and_preview",
                "name": "Geracao local e preview",
                "reusable_for": ["video", "imagem", "landing", "documento", "campanha"],
                "outputs": ["arquivo local", "preview", "relatorio", "gate humano"]
            },
            {
                "id": "human_gate_and_governance",
                "name": "Governanca e OK humano",
                "reusable_for": ["publicacao", "deploy", "envio ao cliente", "IA paga", "acao externa"],
                "outputs": ["decisao", "auditoria", "bloqueio", "aprovacao"]
            },
            {
                "id": "commercial_automation_layer",
                "name": "Camada comercial automatizada",
                "reusable_for": ["telegram", "whatsapp", "site chat", "crm", "relatorios"],
                "outputs": ["atendimento", "captura de lead", "notificacoes", "relatorios diarios"]
            },
            {
                "id": "knowledge_feedback_loop",
                "name": "Ciclo de aprendizagem",
                "reusable_for": ["todos os projetos"],
                "outputs": ["novo skill", "novo playbook", "novo agente", "melhoria de processo"]
            }
        ],
        "vertical_templates": {
            "loja": ["produto", "oferta", "conteudo", "atendimento", "whatsapp", "estoque", "campanha local"],
            "saas": ["persona", "problema", "demo", "landing", "onboarding", "trial", "suporte"],
            "agencia": ["cliente", "briefing", "criativo", "aprovacao", "calendario", "relatorio"],
            "clinica": ["servico", "autoridade", "agenda", "triagem", "conteudo educativo", "compliance"],
            "multinacional": ["marca", "regiao", "governanca", "compliance", "relatorios", "orquestracao multi-time"]
        }
    }

def build_hupmix_case():
    return {
        "status": "KOS_CASE_LEARNING_HUPMIX_V1_READY",
        "case": "Hupmix / Garoto Oxy Power",
        "role": "caso-escola para processos reutilizaveis",
        "specific_assets": [
            "Instagram Hupmix",
            "video real baixado via Meta Graph read-only",
            "Oxy Power 5L",
            "Garoto Oxy",
            "preco R$ 49,90",
            "GP_VIDEO_01",
            "GP_VIDEO_02"
        ],
        "learned_processes": [
            {
                "from_hupmix": "baixar ultimo video do Instagram",
                "universal_pattern": "asset_bridge_public_or_owned_channel",
                "applies_to": ["lojas", "clinicas", "agencias", "saas com redes sociais"]
            },
            {
                "from_hupmix": "criar missao de captacao real",
                "universal_pattern": "real_asset_capture_mission",
                "applies_to": ["produto fisico", "servico local", "depoimento", "case de cliente"]
            },
            {
                "from_hupmix": "gerar preview local com asset real",
                "universal_pattern": "local_preview_generator_before_external_action",
                "applies_to": ["video", "landing", "post", "documento comercial"]
            },
            {
                "from_hupmix": "bloquear publicacao automatica",
                "universal_pattern": "human_gate_for_external_action",
                "applies_to": ["instagram", "whatsapp", "email", "deploy", "ads"]
            },
            {
                "from_hupmix": "usar personagem Garoto Oxy",
                "universal_pattern": "brand_character_or_voice_system",
                "applies_to": ["mascote", "especialista", "fundador", "vendedor virtual"]
            },
            {
                "from_hupmix": "integrar atendimento automatizado futuro",
                "universal_pattern": "business_command_center",
                "applies_to": ["telegram", "whatsapp", "chat no site", "crm", "notificacoes do dono"]
            }
        ],
        "next_evolution": [
            "melhorar qualidade estetica do gerador local",
            "criar EDL para editor humano",
            "criar prompt packs para IA visual quando autorizada",
            "criar templates de campanha por vertical",
            "criar score de qualidade comparavel a Manus"
        ]
    }

def build_campaign_skill():
    return """# KOS Universal Campaign Creator Skill V1

Status: READY

## Regra principal

Nunca tratar um cliente como caso isolado perdido.
Cada campanha deve gerar processo reutilizavel.

## Fluxo universal

1. Entender negocio
2. Identificar oferta principal
3. Auditar canais existentes
4. Coletar assets reais
5. Definir personagem ou voz de marca
6. Criar narrativa curta
7. Criar roteiro por cenas
8. Gerar preview local
9. Pedir OK humano
10. Registrar aprendizado reutilizavel

## Saidas obrigatorias

- briefing
- roteiro
- checklist de assets
- legenda
- plano de edicao
- preview local quando possivel
- status de aprovacao
- aprendizado universal

## Bloqueios

- sem publicacao automatica
- sem deploy automatico
- sem IA paga sem aprovacao
- sem scraping
- sem navegador logado
"""

def build_gp_skill():
    return """# KOS GP Creator Skill V2

Status: READY

## Funcao

Criar conteudos do Garoto Oxy Power como caso-escola de personagem comercial reutilizavel.

## Aprendizado universal

Garoto Oxy nao e apenas um personagem.
Ele representa um padrao: porta-voz comercial com narrativa, oferta, prova visual e CTA.

Esse padrao pode virar:

- mascote de loja
- especialista de clinica
- fundador de SaaS
- vendedor de agencia
- embaixador de marca
- assistente comercial de produto

## Estrutura do video

1. Hook rapido
2. Problema real
3. Produto ou solucao
4. Demonstracao
5. Resultado
6. Oferta
7. CTA

## Regras de qualidade

- usar asset real sempre que existir
- nao inventar prova visual
- separar roteiro de footage
- manter consistencia de personagem
- gerar preview local antes de qualquer publicacao
- salvar aprendizado para outras verticais
"""

def build_automation_skill():
    return """# KOS Business Automation Factory Skill V1

Status: READY

## Funcao

Transformar atendimento, captacao e notificacao comercial em modulo reutilizavel.

## Canais

- Telegram
- WhatsApp
- chat no site
- Instagram read-only ou gateado
- CRM futuro
- relatorios diarios

## Padrao universal

1. Cliente entra por canal
2. IA responde com base no catalogo/contexto
3. Dono recebe notificacao
4. Sistema registra lead
5. Comandos administrativos mostram estado
6. Relatorio diario resume operacao

## Aplicacao por vertical

- loja: produtos, preco, estoque, entrega, WhatsApp
- clinica: servicos, agenda, triagem, orientacao segura
- SaaS: planos, suporte, onboarding, trial
- agencia: leads, briefing, reuniao, proposta
- multinacional: roteamento, compliance, relatorios regionais
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="hupmix")
    parser.add_argument("--mode", default="promote")
    args = parser.parse_args()

    registry = build_registry()
    hupmix_case = build_hupmix_case()

    changed = []
    targets = [
        (KNOWLEDGE / "KOS_UNIVERSAL_PROCESS_REGISTRY.json", registry),
        (KNOWLEDGE / "KOS_CASE_LEARNING_HUPMIX.json", hupmix_case),
    ]

    for path, data in targets:
        if write_json_if_changed(path, data):
            changed.append(rel(path))

    registry_md = "# KOS Universal Process Registry V1\n\nStatus: READY\n\nHupmix e um caso-escola, nao o universo do K-OS.\n\nCada projeto deve alimentar:\n\n- processo reutilizavel\n- skill\n- playbook\n- agente\n- governanca\n\nVerticais iniciais: lojas, SaaS, agencias, clinicas e multinacionais.\n"
    case_md = "# KOS Case Learning — Hupmix\n\nStatus: READY\n\nHupmix gerou padroes reutilizaveis para campanhas, assets reais, personagens comerciais, preview local e human gate.\n\nO aprendizado deve ser reutilizado em outras operacoes.\n"

    text_targets = [
        (KNOWLEDGE / "KOS_UNIVERSAL_PROCESS_REGISTRY.md", registry_md),
        (KNOWLEDGE / "KOS_CASE_LEARNING_HUPMIX.md", case_md),
        (SKILLS / "KOS_UNIVERSAL_CAMPAIGN_CREATOR_SKILL_V1.md", build_campaign_skill()),
        (SKILLS / "KOS_GP_CREATOR_SKILL_V2.md", build_gp_skill()),
        (SKILLS / "KOS_BUSINESS_AUTOMATION_FACTORY_SKILL_V1.md", build_automation_skill()),
    ]

    for path, content in text_targets:
        if write_text_if_changed(path, content):
            changed.append(rel(path))

    policy = {
        "status": "KOS_KNOWLEDGE_EXPANSION_POLICY_V1_READY",
        "version": "v1",
        "rule": "Todo modulo criado para um cliente deve ser classificado em especifico, reutilizavel ou runtime.",
        "classification": {
            "case_specific": "marca, produto, cliente, campanha, ativo local",
            "reusable": "processo, skill, checklist, gerador, agente, template",
            "runtime": "execucao, preview, log, last_run, arquivos temporarios"
        },
        "mandatory_question_after_each_module": "O que isso ensina ao K-OS para outros negocios?"
    }

    if write_json_if_changed(GOV / "KOS_KNOWLEDGE_EXPANSION_POLICY_V1.json", policy):
        changed.append(rel(GOV / "KOS_KNOWLEDGE_EXPANSION_POLICY_V1.json"))

    report = {
        "status": "KOS_PROCESS_LEARNING_ENGINE_V1_READY",
        "version": "v1",
        "case_seed": "hupmix",
        "purpose": "Transformar casos especificos em conhecimento operacional reutilizavel.",
        "created_memory": [
            "memory/kos_knowledge/KOS_UNIVERSAL_PROCESS_REGISTRY.json",
            "memory/kos_knowledge/KOS_CASE_LEARNING_HUPMIX.json",
            "memory/kos_skills/KOS_UNIVERSAL_CAMPAIGN_CREATOR_SKILL_V1.md",
            "memory/kos_skills/KOS_GP_CREATOR_SKILL_V2.md",
            "memory/kos_skills/KOS_BUSINESS_AUTOMATION_FACTORY_SKILL_V1.md",
            "memory/kos_governance/KOS_KNOWLEDGE_EXPANSION_POLICY_V1.json"
        ],
        "next_step": "Conectar novos pedidos ao processo universal antes de criar solucao especifica."
    }

    write_json_if_changed(REPORTS / "KOS_PROCESS_LEARNING_ENGINE_V1.json", report)
    write_text_if_changed(
        REPORTS / "KOS_PROCESS_LEARNING_ENGINE_V1.md",
        "# KOS Process Learning Engine V1\n\nStatus: READY\n\nHupmix virou caso-escola. O K-OS agora registra processos universais para outras verticais.\n"
    )

    runtime = {
        "status": "KOS_PROCESS_LEARNING_ENGINE_RUN_READY",
        "created_at": datetime.now().isoformat(),
        "case": args.case,
        "mode": args.mode,
        "changed_tracked_files": changed,
        "registry": "memory/kos_knowledge/KOS_UNIVERSAL_PROCESS_REGISTRY.json",
        "hupmix_case_learning": "memory/kos_knowledge/KOS_CASE_LEARNING_HUPMIX.json",
        "next_step": "Usar o orquestrador para aplicar esse padrao a proximo cliente, vertical ou produto."
    }

    (RUNTIME / "status.json").write_text(json.dumps(runtime, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(runtime, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
