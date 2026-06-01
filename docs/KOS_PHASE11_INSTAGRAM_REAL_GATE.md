# K-OS Fase 11 Instagram Real Publisher Gate

Objetivo: preparar a primeira ponte real de publicacao no Instagram.

Variaveis locais esperadas:
- IG_BUSINESS_ACCOUNT_ID
- META_ACCESS_KEY
- KOS_REAL_IG_PUBLISH_ENABLED
- KOS_HUMAN_OK_FOR_IG_REAL

Regra:
- Sem ambiente completo: bloqueia.
- Sem flag real: bloqueia.
- Sem OK humano final: bloqueia.
- Com tudo ativo: executa publicacao real.

Esta fase cria o gate. O primeiro teste real deve ser feito na Fase 12 com um post controlado.
