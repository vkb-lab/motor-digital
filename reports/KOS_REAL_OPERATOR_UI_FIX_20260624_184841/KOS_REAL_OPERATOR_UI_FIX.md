# KOS REAL OPERATOR UI FIX

Data: 20260624_184841

## Diagnóstico real

A tela ainda mostra o fluxo técnico antigo antes da resposta operacional.

O usuário está vendo:
- O que posso acionar agora
- Safe Action / Human Gate
- Registry READY
- Action Packet
- Guardrails ativos
- Nada foi publicado

Isso deve sair da resposta principal.

## Correção obrigatória

No arquivo:

pages/KOS_Operator_Chat.py

A resposta principal deve usar:

from scripts.kos_real_operator_response_composer import compose_for_chat

E renderizar:

result = compose_for_chat(raw_response, root=PROJECT_ROOT)
st.markdown(result["user_response"])

A resposta técnica deve ir para:

with st.expander("Detalhes técnicos", expanded=False):
    st.code(result["technical_evidence"])

## Regra

A tela principal deve mostrar primeiro:

Instagram conectado operacionalmente agora: Hupmix.
Casa da Limpeza está registrada localmente.
Parada Atlântida está travada para ação externa.
Hupmix responde via Meta Graph como @hupmix.
Mídias no perfil: 30.
Mídias recentes lidas: 5.

Próximos pedidos:
- revisar última publicação;
- gerar legenda melhor;
- comparar últimas 5 postagens.

## Não mostrar no corpo principal

- Safe Action
- Human Gate
- Action Packet
- Registry READY
- Guardrails ativos
- Nada foi publicado
- caminho .json

## Arquivos criados agora

- scripts/kos_real_operator_response_composer.py
- tests/test_kos_real_operator_response_composer.py

## Próximo passo

Aplicar o composer no ponto de renderização da resposta em pages/KOS_Operator_Chat.py.

Use o leak map:
reports\KOS_REAL_OPERATOR_UI_FIX_20260624_184841\01_operator_chat_leak_map.txt
