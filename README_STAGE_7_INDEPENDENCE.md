# Etapa 7/9 - Setembro Independencia

Objetivo:
preparar independencia operacional do K-Atlas sem liberar publicacao irresponsavel.

Estado inicial:
- Render online
- GitHub como fonte de deploy
- cockpit supervisionado
- auto publish bloqueado
- APIs externas bloqueadas por padrao

Checkpoint desta etapa:
Credential Vault + Test Page API Adapter.

Regras:
- Nao salvar token em texto puro.
- Nao commitar .env.
- Nao publicar em conta oficial.
- Nao enviar mensagem em massa.
- Nao operar navegador automaticamente.
- API externa so pode rodar com K_SOCIAL_EXTERNAL_API_ENABLED=true.
- Auto publish deve permanecer false.
- Todo envio de teste precisa de aprovacao humana e audit log.

Variaveis futuras no Render:
K_SOCIAL_EXTERNAL_API_ENABLED=false
K_SOCIAL_AUTO_PUBLISH=false
K_SOCIAL_TEST_PAGE_ENDPOINT=valor secreto
K_SOCIAL_TEST_PAGE_TOKEN=valor secreto

Padrao de referencia:
vault://env/NOME_DA_VARIAVEL