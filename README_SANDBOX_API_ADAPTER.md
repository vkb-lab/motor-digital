# Checkpoint 36 - Sandbox API Adapter

Simula integrações externas sem chamar API real.

## Providers

- google_ai_sandbox
- meta_graph_sandbox
- whatsapp_cloud_sandbox
- email_sandbox

## Regras

- Sem rede externa.
- Sem token.
- Sem publicação.
- Sem mensagem em massa.
- Sem browser automation.
- Segredo em texto puro é bloqueado.
- API real futura exige Credential Vault.

## Página

pages/17_K_Atlas_Sandbox_API_Adapter.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_sandbox_api_adapter_smoke.ps1"
