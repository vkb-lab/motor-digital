# Checkpoint 35 - Credential Vault

Prepara o K-Atlas para credenciais seguras sem salvar tokens em texto puro.

## Regras

- Segredo real fica em variável de ambiente.
- Código usa referência: vault://env/NOME_DA_VARIAVEL
- Token nunca é impresso.
- Token nunca é salvo em JSON.
- API externa futura exige credential_vault_ref.
- Publicação oficial continua bloqueada até Level 4.

## Página

pages/16_K_Atlas_Credential_Vault.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\check_credential_vault.ps1"

## Render

Configurar credenciais em:
Environment -> Environment Variables

Exemplos futuros:
- GOOGLE_AI_API_KEY
- META_GRAPH_ACCESS_TOKEN
- WHATSAPP_CLOUD_API_TOKEN
- OPENAI_API_KEY
