# ⚡ Motor Digital Multitenant

Bem-vindo ao repositório do **Motor Digital Multitenant**, um sistema avançado de gestão operacional com inteligência artificial embarcada. Este projeto foi concebido para centralizar e automatizar fluxos de trabalho de múltiplos negócios através de uma interface moderna, ágil e *mobile-friendly*.

---

## 🧠 Arquitetura de Inteligência Central: Gemini 1.5 Pro

A espinha dorsal deste sistema é a sua inteligência central. Diferente de arquiteturas fragmentadas que dependem de múltiplos agentes de terceiros, o Motor Digital orquestra **todas as suas capacidades analíticas e generativas através da API do Gemini 1.5 Pro** via Google AI Studio.

Esta abordagem arquitetural garante:
- **Independência Tecnológica:** Redução drástica da dependência de plataformas de automação e agentes externos, mantendo o controle total sobre o processamento de dados.
- **Contexto Unificado:** A IA possui visão holística de todas as operações (Meta, Portal, Workspace), permitindo correlações complexas e geração de *insights* estratégicos superiores.
- **Escalabilidade:** A capacidade multitenant aliada ao modelo Gemini 1.5 Pro suporta o crescimento exponencial do volume de dados e operações sem gargalos de orquestração.
- **Processamento de Contexto Longo:** O Gemini 1.5 Pro é capaz de processar janelas de contexto massivas, o que o torna ideal para analisar históricos de vendas, interações com clientes e relatórios complexos em uma única requisição.

## 📱 Estrutura do Aplicativo

O aplicativo foi desenvolvido em Python utilizando a biblioteca **Streamlit**, otimizado com CSS customizado para garantir uma experiência de uso fluida em dispositivos móveis. A navegação é dividida em 4 abas principais:

### 1. 🏠 Painel Geral
O centro de comando. Exibe métricas consolidadas em tempo real (leads, receita, tarefas) e fornece acesso direto ao Assistente Gemini para consultas estratégicas e *insights* instantâneos sobre o negócio.

### 2. 📣 Operações Meta (Multitenant)
Gerenciador centralizado de campanhas e conteúdo para diferentes operações. Atualmente suporta:
- **Parada Atlântida (Florianópolis):** Foco em turismo, gastronomia, geolocalização e cupons de experiência.
- **Casa da Limpeza (Antônio Carlos):** Foco em vendas B2B, tabelas de preço e orçamentos corporativos automatizados.
Possui integração com o Gemini para geração autônoma de legendas de redes sociais adaptadas ao tom de voz de cada marca.

### 3. 🌐 Portal Atlântida
Aba dedicada à gestão da plataforma de turismo e *cashback*. Monitora o engajamento dos usuários, ranking de gamificação, distribuição de *cashback* e performance dos parceiros cadastrados. Inclui geração de relatórios de engajamento orientados por IA.

### 4. 🗂️ Workspace
O ambiente de produtividade do gestor. Centraliza a triagem inteligente de e-mails (com resumos e sugestões de respostas geradas pelo Gemini) e a gestão da agenda diária, preparando o terreno para futuras integrações diretas com Gmail API e Google Calendar.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior
- Chave de API do Google AI Studio (Gemini)

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/vkb-lab/motor-digital.git
   cd motor-digital
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Configure a chave da API do Gemini. No terminal, execute:
   ```bash
   export GEMINI_API_KEY="sua_chave_aqui"
   ```

4. **Execute o aplicativo:**
   ```bash
   streamlit run app.py
   ```

---

## 📦 Dependências Principais (`requirements.txt`)

- `streamlit`: *Framework* para criação da interface web.
- `google-genai`: SDK oficial para integração com os modelos do Google AI Studio.
- `pandas`: Manipulação e estruturação de dados em DataFrames.
- `requests`: Para chamadas HTTP nativas à API do Gemini (caso não se utilize o SDK).

---
*Projeto mantido por vkb-lab. Motor Digital — Inteligência a serviço da escala.*
