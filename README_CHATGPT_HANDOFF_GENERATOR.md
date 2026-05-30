# K-Atlas ChatGPT Handoff Generator

Gera um prompt de continuidade operacional para colar no ChatGPT.

## Faz

- lê sinais locais do K-Atlas
- resume o estado operacional
- cria prompt de continuidade
- salva em memory/chatgpt_handoff
- gera relatório em reports/chatgpt_handoff
- copia o prompt para a área de transferência

## Não faz

- não automatiza navegador
- não move mouse
- não chama API externa
- não publica
- não faz deploy
- não executa ação externa

## Uso

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\generate_k_atlas_chatgpt_handoff.ps1"
