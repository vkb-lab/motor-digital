# Dados Sensíveis e Segurança

## O que são dados sensíveis no K-OS

Dados sensíveis são qualquer informação que permita acesso, controle, identificação, publicação, pagamento, rastreamento ou exposição indevida.

Incluem:

- tokens de API;
- access tokens Meta;
- OAuth Google;
- client secrets;
- cookies;
- senhas;
- chaves privadas;
- arquivos .env;
- segredos Streamlit;
- dados de clientes;
- conversas comerciais;
- dados pessoais;
- documentos internos;
- estratégias de negócio;
- campanhas ainda não publicadas;
- leads;
- relatórios financeiros;
- credenciais de GitHub;
- credenciais de WhatsApp, Telegram, Google, Meta ou ManyChat.

## Política

O K-OS nunca deve expor valores de segredo.

Ele pode informar:

- existe;
- não existe;
- está versionado por erro;
- está fora do Git;
- precisa ser rotacionado;
- precisa de Human Gate.

Mas nunca deve imprimir o valor real.

## Onde ficam os dados sensíveis

Preferencialmente:

- local_runtime/kos_secrets/
- .env local ignorado pelo Git
- secrets manager futuro
- variáveis de ambiente

Nunca devem ir para:

- reports/
- memory/
- GitHub;
- logs públicos;
- screenshots;
- resposta do chat.

## Ações externas

São bloqueadas por padrão:

- publicar post;
- enviar mensagem;
- fazer deploy;
- usar IA paga;
- fazer scraping;
- automatizar navegador logado;
- apagar dados;
- alterar conta externa;
- mexer em produção.

Exigem Human Gate explícito.
