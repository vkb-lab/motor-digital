# KOS SKILL — GOOGLE AI TOOLBELT OPERATOR V1

Status: skill interna oficial  
Funcao: ensinar o K-OS a usar ferramentas Google como arsenal operacional dos projetos Kaizen

---

## 1. Objetivo

Esta skill transforma as ferramentas Google em um toolbelt orquestrado pelo K-OS.

O K-OS deve saber quando usar:

- Google AI Studio;
- Gemini API;
- Gmail Operator;
- Google Stitch;
- Pomelli;
- Opal;
- Mixboard;
- Google Flow;
- Google Flow Music / ProducerAI;
- Google Antigravity;
- NotebookLM.

---

## 2. Regra principal

O K-OS nao deve tratar tudo como API.

Existem tres tipos de ferramenta:

### API real

Pode ser chamada por script, token ou SDK.

Exemplos:
- Gemini API;
- Gmail API.

### OAuth/Google Workspace

Depende de consentimento do usuario e escopo.

Exemplos:
- Gmail conectado;
- Drive/Docs/Calendar futuros.

### Browser-assisted / Human-in-the-loop

Ferramenta usada por navegador, com prompt, upload, export e registro de resultado.

Exemplos:
- Stitch;
- Pomelli;
- Opal;
- Mixboard;
- Flow;
- Flow Music / ProducerAI;
- NotebookLM;
- Antigravity.

---

## 3. Ciclo de uso

Quando o operador pedir uma solucao, o K-OS deve:

1. entender objetivo;
2. identificar projeto;
3. consultar Baú;
4. escolher ferramenta Google adequada;
5. gerar prompt ou briefing;
6. abrir rota de execucao;
7. registrar input;
8. registrar output;
9. transformar resultado em ativo;
10. salvar relatorio;
11. sugerir proximo passo.

---

## 4. Mapa de ferramentas por tipo de tarefa

### UI e produto

Usar:
- Stitch;
- AI Studio;
- Antigravity.

Saida:
- telas;
- fluxos;
- componentes;
- prototipo;
- handoff tecnico.

### Marketing e marca

Usar:
- Pomelli;
- Mixboard;
- Flow;
- Flow Music / ProducerAI.

Saida:
- campanha;
- post;
- moodboard;
- roteiro;
- video;
- musica;
- sonic branding.

### Pesquisa e pitch

Usar:
- NotebookLM;
- Gemini;
- Gmail reports;
- Baú.

Saida:
- resumo com fontes;
- material para startup;
- argumentos para subsidio;
- matriz de oportunidades.

### Desenvolvimento

Usar:
- Antigravity;
- AI Studio;
- GitHub;
- Supabase;
- K-OS.

Saida:
- codigo;
- testes;
- logs;
- deploy;
- artefatos de validacao.

---

## 5. Regra para subsidy/startup

Quando o objetivo for disputar subsidio, pitch, incentivo ou programa de startup, o K-OS deve montar um pacote com:

1. problema;
2. solucao;
3. arquitetura;
4. uso de Google Cloud;
5. uso de Gemini/API;
6. uso de Google Workspace;
7. uso de Labs/creative AI;
8. demo;
9. seguranca;
10. impacto comercial;
11. roadmap;
12. evidencias.

---

## 6. Guardrails

Nunca:
- commitar API keys;
- commitar OAuth tokens;
- fingir API onde so existe UI;
- publicar asset sem revisao;
- usar ferramenta paga sem autorizacao;
- automatizar navegador logado sem autorizacao explicita;
- misturar prototipo com producao.

Sempre:
- separar resposta principal de evidencia tecnica;
- salvar prompt e output;
- registrar projeto/tenant;
- versionar apenas memoria sanitizada;
- manter Human Gate para publish/send/delete/deploy/pago.

---

## 7. Resposta padrao do K-OS

Quando receber um pedido amplo, responder:

"Vou processar com Google AI Toolbelt: verifico o objetivo, escolho a ferramenta certa, preparo prompt/briefing, registro o resultado no Baú e transformo a saida em ativo executavel do projeto."

---

## 8. Proximo passo ideal

Criar um painel/bridge no Operator Chat chamado:

Google AI Toolbelt

Com botoes:
- Stitch UI
- Pomelli Campaign
- Opal Mini-App
- Mixboard Concept
- Flow Video
- Flow Music
- NotebookLM Research
- Antigravity Build
- AI Studio Gemini
