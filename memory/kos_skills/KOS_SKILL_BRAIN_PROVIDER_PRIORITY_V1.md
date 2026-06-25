# KOS SKILL — BRAIN PROVIDER PRIORITY V1

Status: skill interna oficial

## Objetivo

Definir como o K-OS escolhe inteligência/modelo antes de gastar token, chamar API externa ou usar ferramenta paga.

## Ordem obrigatória

1. Inteligência interna evolutiva do K-OS.
2. IA local gratuita instalada no computador.
3. IA cloud gratuita ou com quota diária.
4. Provedor externo pago/sensível somente com aprovação.

## Regra 1 — consultar o K-OS primeiro

Antes de chamar qualquer LLM externo, o K-OS deve consultar:

- Baú;
- registries;
- políticas;
- estado do Git;
- relatórios existentes;
- OrchestratorAgent;
- Brain Gateway;
- conectores ativos.

Se a resposta puder ser resolvida com conhecimento interno e estado local, não usar tokens externos.

## Regra 2 — usar IA local gratuita primeiro

Se o problema exigir geração/raciocínio e houver IA local funcionando, priorizar:

- Ollama;
- LM Studio;
- LocalAI;
- vLLM;
- outro servidor local OpenAI-compatible.

O K-OS só pode dizer que uma IA local está ativa se:

- executável ou endpoint foi encontrado;
- healthcheck respondeu;
- existe modelo disponível;
- resultado foi registrado.

## Regra 3 — usar quota gratuita cloud antes de pago

Gemini Free Guarded entra antes de qualquer provedor pago quando:

- GEMINI_API_KEY existe;
- KOS_AI_GEMINI_ENABLED=true;
- orçamento diário local não foi excedido;
- tarefa justifica modelo cloud.

O K-OS não deve hardcodar limites oficiais. Limites mudam por modelo, tier e conta.

## Regra 4 — paid/external bloqueado

OpenAI, Anthropic, Runway, ElevenLabs, Luma, Sora e similares ficam bloqueados por padrão.

Exigem:

- vault;
- orçamento;
- escopo;
- Human Gate;
- log de provider;
- motivo da chamada.

## Resposta padrão quando perguntarem “qual IA você está usando?”

O K-OS deve responder:

- primeiro consultei inteligência interna;
- verifiquei IA local gratuita;
- verifiquei quota cloud gratuita;
- não usei provider pago sem autorização.

## Critério de escalada

Escalar para provider superior apenas se:

- contexto interno insuficiente;
- modelo local ausente/fraco;
- tarefa exige capacidade cloud;
- benefício supera custo/risco;
- guardrails permitem.
