from k_atlas.core.cowork_response import CoworkResponse


def route_intent(command: str) -> CoworkResponse:
    text = (command or "").strip()
    low = text.lower()

    if not text:
        return CoworkResponse(
            understanding="Você ainda não escreveu um comando.",
            plan=["Digite o que quer resolver agora."],
            next_step="Escreva um pedido como: analise minha área de trabalho, abra o Gmail ou crie um projeto.",
            intent="empty",
            action="none",
        )

    # Gmail / email
    if "gmail" in low or "email" in low or "e-mail" in low or "emails" in low or "e-mails" in low:
        return CoworkResponse(
            understanding=f"Você quer que eu trabalhe com seus emails: '{text}'.",
            plan=[
                "Identificar se o pedido é apenas abrir o Gmail ou ler mensagens.",
                "Abrir o Gmail se for uma ação local possível.",
                "Para ler e resumir emails, usar integração Gmail API/OAuth.",
                "Nunca enviar ou responder email sem confirmação explícita."
            ],
            executed=[],
            blocked=[
                "Abrir o Gmail é possível agora.",
                "Ler emails de verdade exige integração Gmail API/OAuth autorizada.",
                "No modo atual, eu não devo fingir que li emails se apenas abri o navegador."
            ],
            next_step="Posso abrir o Gmail agora. Para verificar emails de ontem e resumir, precisamos conectar Gmail API ao K-Atlas.",
            intent="gmail_check",
            action="open_gmail",
            metadata={"url": "https://mail.google.com"}
        )

    # Instagram
    if "instagram" in low or "insta" in low:
        return CoworkResponse(
            understanding=f"Você quer trabalhar com Instagram: '{text}'.",
            plan=[
                "Abrir Instagram se o pedido for acesso.",
                "Se for criação de conteúdo, preparar campanha/legenda/calendário.",
                "Publicação automática exigirá integração Meta/Instagram Graph API."
            ],
            next_step="Posso abrir o Instagram agora ou criar um plano de conteúdo.",
            intent="instagram",
            action="open_instagram",
            metadata={"url": "https://www.instagram.com"}
        )

    # Canva
    if "canva" in low:
        return CoworkResponse(
            understanding=f"Você quer usar o Canva: '{text}'.",
            plan=[
                "Abrir Canva.",
                "Definir tipo de arte.",
                "Organizar briefing de criação.",
                "Preparar textos, medidas e orientação visual."
            ],
            next_step="Posso abrir o Canva e preparar o briefing da arte.",
            intent="canva",
            action="open_canva",
            metadata={"url": "https://www.canva.com"}
        )

    # Janelas
    if "janela" in low or "janelas" in low:
        return CoworkResponse(
            understanding="Você quer verificar as janelas abertas no Windows.",
            plan=["Detectar janelas abertas.", "Mostrar resultado limpo na lousa."],
            intent="windows_list",
            action="list_windows"
        )

    # Área de trabalho
    if "área de trabalho" in low or "area de trabalho" in low or "desktop" in low:
        return CoworkResponse(
            understanding="Você quer analisar sua Área de Trabalho.",
            plan=[
                "Mapear arquivos da Área de Trabalho.",
                "Classificar por tipo.",
                "Gerar relatório.",
                "Sugerir organização sem mover nada."
            ],
            next_step="Vou gerar um relatório antes de qualquer ação.",
            intent="desktop_analysis",
            action="analyze_desktop"
        )

    # Criar projeto
    if "crie um projeto" in low or "criar projeto" in low or "novo projeto" in low:
        return CoworkResponse(
            understanding=f"Você quer criar um novo projeto: '{text}'.",
            plan=[
                "Extrair nome provável do projeto.",
                "Criar pasta no workspace.",
                "Criar README inicial.",
                "Registrar no K-Atlas."
            ],
            next_step="Vou criar uma estrutura inicial segura no workspace.",
            intent="create_project",
            action="create_project"
        )

    # Criar app
    if "crie um app" in low or "criar app" in low or "aplicativo" in low or "sistema" in low:
        return CoworkResponse(
            understanding=f"Você quer transformar uma ideia em aplicativo/sistema: '{text}'.",
            plan=[
                "Entender objetivo do app.",
                "Definir páginas principais.",
                "Definir banco de dados.",
                "Sugerir stack.",
                "Criar plano técnico inicial."
            ],
            next_step="Vou gerar um plano de aplicativo antes de criar arquivos.",
            intent="app_builder",
            action="generate_app_plan"
        )

    # Padrão
    return CoworkResponse(
        understanding=f"Recebi seu pedido: '{text}'.",
        plan=[
            "Interpretar intenção.",
            "Verificar se existe ação local segura.",
            "Executar somente o que for seguro.",
            "Explicar bloqueios quando precisar de API, senha ou permissão."
        ],
        next_step="Ainda preciso de uma rota específica para esse tipo de comando.",
        intent="general",
        action="explain"
    )
