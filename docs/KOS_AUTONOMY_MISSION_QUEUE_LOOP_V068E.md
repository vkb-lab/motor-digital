# K-OS Mission Queue Loop v0.68E

## Loop persistente

powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomy_mission_queue_loop.ps1

## Smoke único

powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomy_mission_queue_loop.ps1 -Once

## Regras

- Processa a fila criada na 68D.
- Respeita Kill Switch.
- Usa Mission Queue Processor.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
