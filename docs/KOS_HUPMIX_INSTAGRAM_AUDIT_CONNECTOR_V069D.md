# K-OS Hupmix Instagram Audit Connector v0.69D

Objetivo:
Conectar somente a conta teste Hupmix via Meta Graph API e gerar auditoria read-only.

Conta permitida:
- username: hupmix
- ig_id: 17841471706662294

Regras:
- Somente GET.
- Nao publica.
- Nao envia mensagem.
- Nao usa navegador logado.
- Nao imprime token.
- Parada Atlantida continua bloqueada.
- Qualquer conta diferente de hupmix bloqueia a auditoria.

Comando:
python scripts\run_phase69d_hupmix_instagram_audit.py
