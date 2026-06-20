# K-OS ChatGPT Bridge Drop Watcher v0.70D

Objetivo:
Transformar a pasta drop da ponte ChatGPT em uma entrada operacional contínua para pacotes do K-Atlas Engineer.

O que faz:
- observa arquivos .txt em local_runtime/kos_chatgpt_bridge/drop
- valida marcadores KOS_ENGINEER_PACKET_START/END
- bloqueia termos perigosos
- processa via 69K one-click
- gera revisão via 69L
- registra eventos

O que não faz:
- não automatiza navegador logado
- não faz scraping do ChatGPT
- não lê cookies
- não clica sozinho
- não aplica patch
- não publica
- não executa ação perigosa automaticamente

Abrir watcher:
KOS_ChatGPT_Bridge_Drop_Watcher.cmd

Tick único:
powershell -ExecutionPolicy Bypass -File scripts\start_kos_chatgpt_bridge_drop_watcher.ps1 -Once
