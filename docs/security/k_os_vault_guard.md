# K-OS Vault Guard

Checkpoint 018.

Objetivo:

- criar cofre local de chaves
- impedir token no codigo
- impedir credenciais no GitHub
- preparar APIs externas com seguranca
- registrar auditoria sem expor valores

Armazenamento local:

local_secrets/k_os_vault/vault.json

Esse caminho deve permanecer ignorado pelo Git.

Protecao:

O cofre usa Windows DPAPI por usuario local via PowerShell ConvertFrom-SecureString.

Regra:

Nenhum agente acessa chaves diretamente.

Agentes podem apenas solicitar uso futuro via approval gate, Security Council, Credential Vault Policy e External API Sandbox.

Provedores futuros:

- OpenAI
- Runway
- ElevenLabs
- Instagram
- WhatsApp
- Google
- GitHub
- Luma
- Sora
- Midjourney
- ComfyUI

Comandos:

Inicializar:
powershell -ExecutionPolicy Bypass -File ".\ops\k_os_vault_guard.ps1" -Action Init

Auditar:
powershell -ExecutionPolicy Bypass -File ".\ops\k_os_vault_guard.ps1" -Action Audit

Adicionar chave sem expor no historico:
powershell -ExecutionPolicy Bypass -File ".\ops\k_os_vault_guard.ps1" -Action SetItem -Provider "openai" -Name "primary"

Listar metadados:
powershell -ExecutionPolicy Bypass -File ".\ops\k_os_vault_guard.ps1" -Action List

Remover item:
powershell -ExecutionPolicy Bypass -File ".\ops\k_os_vault_guard.ps1" -Action DeleteItem -Provider "openai" -Name "primary"

Politica:

- nao exibir valor bruto
- nao commitar cofre
- nao publicar externamente
- nao enviar externamente
- toda ativacao real exige aprovacao humana