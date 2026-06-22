# K-OS Hupmix Instagram Continuity Audit

Status: KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT_READY

## Politica
- meta_graph_read_only: True
- no_scraping: True
- no_logged_browser_automation: True
- no_publish: True
- no_delete: True
- no_comment: True
- no_dm: True
- no_paid_ai: True
- human_gate_required: True

## Estado local
- production_kit_json: True | campaigns/hupmix_gp_recovery/GP_VIDEO_01_PRODUCTION_KIT.json
- video_factory_job: True | campaigns/hupmix_gp_recovery/GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json
- local_preview_mp4: True | local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4
- local_storyboard: True | local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_STORYBOARD.png
- human_review_approval: False | live/human_decision_center/hupmix_gp_video_01_publication_review_approval.json

## Instagram
- fetch_status: KOS_HUPMIX_INSTAGRAM_FETCH_READY
- media_type: VIDEO
- timestamp: 2026-03-20T15:35:22+0000
- permalink: https://www.instagram.com/reel/DWHGjCBjLB1/
- caption_score: 9
- caption_hits: oxy, oxy power, limpeza, oxigênio ativo, sem cloro, 5l, 49,90, hupmix, whatsapp
- download_status: KOS_HUPMIX_MEDIA_DOWNLOADED
- download_path: local_runtime/kos_instagram_audit/hupmix/20260622_144446/18087817444971023.mp4

## Interpretacao
- where_project_stopped: GP_VIDEO_01 possui preview MP4 local e job Video Factory. Proximo passo natural: comparar com Instagram Hupmix e registrar decisao humana.
- instagram_latest_status: A ultima publicacao Hupmix parece relacionada ao GP/Oxy Power pelos termos da legenda.
- recommended_next_action: Abrir revisao Hupmix, validar a publicacao baixada e registrar OK humano antes de qualquer proxima campanha.
- requires_human_ok: True
- can_act_without_publish: True

## Proxima acao segura
Abrir revisao Hupmix, validar a publicacao baixada e registrar OK humano antes de qualquer proxima campanha.