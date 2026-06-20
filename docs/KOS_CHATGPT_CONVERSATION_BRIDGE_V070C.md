# K-OS ChatGPT Conversation Bridge v0.70C

Objetivo:
Criar uma ponte segura entre a conversa do K-Atlas Engineer no ChatGPT e o K-OS local.

O que faz:
- abre a conversa oficial no navegador
- abre a pasta de drop local
- permite salvar pacotes Engineer como .txt
- processa o pacote via 69K
- gera revisão via 69L

O que não faz:
- não automatiza navegador logado
- não lê cookies
- não faz scraping da UI do ChatGPT
- não clica sozinho
- não executa ação perigosa automaticamente
- não publica
- não usa IA paga

Fluxo:
1. Abrir KOS_ChatGPT_Conversation_Bridge.cmd
2. ChatGPT abre no navegador
3. Pasta drop abre no Windows
4. Salvar pacote .txt dentro de local_runtime/kos_chatgpt_bridge/drop
5. Rodar:

powershell -ExecutionPolicy Bypass -File scripts\run_kos_chatgpt_conversation_bridge.ps1 -ProcessLatest

Saída:
local_runtime/kos_engineer_packet_review/latest_engineer_packet_review.json
