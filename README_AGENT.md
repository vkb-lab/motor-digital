# 🤖 Motor Digital — Agente Autônomo Local (Core)

Este módulo é o "cérebro" que roda diretamente no seu computador (Windows). Diferente do dashboard web, este agente tem permissão para interagir com o seu Sistema Operacional, gerenciar arquivos e automatizar tarefas de interface.

## 🚀 Capacidades Atuais
1.  **Acesso ao Sistema:** Cria pastas, organiza arquivos e executa comandos de terminal.
2.  **Autoevolução:** Capacidade de ler o próprio código e solicitar melhorias ao Gemini 1.5 Pro.
3.  **Social Bridge:** Estrutura base para automação de postagens em múltiplos perfis de Instagram via Selenium/PyAutoGUI.
4.  **Pesquisa Raiz:** Busca informações no "universo de dados" e cria novos módulos funcionais automaticamente.

## 🛠️ Como Ativar no Windows

### 1. Preparação do Ambiente
Abra o PowerShell no seu HD Externo e execute:
```powershell
# Entrar na pasta
cd motor-digital

# Criar ambiente isolado
python -m venv venv
.\venv\Scripts\activate

# Instalar dependências de automação
pip install -r requirements.txt
```

### 2. Configuração da "Chave Mestra"
Você precisa definir sua chave do Gemini para que o agente possa "pensar":
```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

### 3. Execução do Core
Para iniciar o agente em modo de escuta:
```powershell
python agent_core.py
```

## 🧠 Filosofia Autoevolutiva
O arquivo `self_evolution.py` permite que você dê comandos como:
*"Agente, pesquise como integrar com a API do WhatsApp e crie um módulo para isso."*

O agente irá:
1.  Pesquisar a documentação.
2.  Escrever o código Python.
3.  Testar a execução.
4.  Incorporar a nova habilidade ao sistema principal.

---
**Aviso de Segurança:** Este agente tem permissão para executar comandos no seu computador. Use-o sempre dentro da pasta dedicada no seu HD Externo.
