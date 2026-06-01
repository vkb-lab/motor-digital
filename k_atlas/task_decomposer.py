def decompose_command(command: str, client_id: str = "parada_atlantida"):
    return [
        {"task_id": "campaign", "title": "Criar campanha", "agent": "CampaignStrategistAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "landing_page", "title": "Criar landing page", "agent": "LandingPageAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "qr_code", "title": "Criar QR Code", "agent": "QRLeadAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "instagram_post", "title": "Preparar post Instagram", "agent": "ContentCreatorAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "creative", "title": "Criar criativo visual", "agent": "MediaEditorAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "publication_queue", "title": "Preparar fila de publicacao", "agent": "PublicationQueueAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "audit", "title": "Auditar resultado", "agent": "QualityAuditorAgent", "status": "PENDING_APPROVAL"},
        {"task_id": "final_review", "title": "Gerar aprovacao final", "agent": "FinalApprovalAgent", "status": "PENDING_APPROVAL"},
    ]
