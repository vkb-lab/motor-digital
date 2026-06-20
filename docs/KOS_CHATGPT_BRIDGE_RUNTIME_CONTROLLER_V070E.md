# K-OS ChatGPT Bridge Runtime Controller v0.70E

Controla o watcher da ponte ChatGPT.

Comandos:
powershell -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action start
powershell -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action status
powershell -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action stop
powershell -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action restart
powershell -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action logs

Garantias:
- nao faz scraping do ChatGPT
- nao automatiza navegador logado
- nao publica
- nao aplica patch
- usa trava anti-duplicacao
