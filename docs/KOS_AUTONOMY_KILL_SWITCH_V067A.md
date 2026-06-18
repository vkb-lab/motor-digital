# K-OS Autonomy Kill Switch v0.67A

## Parada emergencial

powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action engage -Reason "operator emergency stop"

## Reativacao manual

powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action disengage -Reason "operator restore" -RestartRuntime

## Status

powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action status

## Regras

- Bloqueia startup enquanto engajado.
- Para loops locais reconhecidos.
- Nao publica Instagram.
- Nao chama IA paga.
- Nao usa navegador logado.
