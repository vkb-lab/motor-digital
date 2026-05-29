# K-Social Publishing Gateway

Modulo de autonomia progressiva para o K-Social Intelligence System.

## Objetivo

Criar um gateway governado entre campanha aprovada e execucao em canal.

Este modulo nao publica em conta oficial.

Ele prepara:
- dry run realista
- pagina de teste local
- fila de publicacao
- permissoes por canal
- aprovacao humana
- logs auditaveis
- bloqueio contra spam
- base futura para Instagram, WhatsApp, e-mail e cockpit

## Nivel recomendado agora

Nivel operacional atual: LEVEL 2 - pagina de teste / sandbox.

Nivel preparado, mas bloqueado por governanca: LEVEL 2.5 - adaptador real de teste com credenciais controladas.

## Regras duras

- Nao usar API real sem credential vault.
- Nao salvar token em texto puro.
- Nao enviar mensagem em massa.
- Nao automatizar navegador.
- Nao publicar em conta oficial.
- Toda acao relevante gera evento auditavel.

## Execucao

python -m k_atlas.social.publishing_gateway.smoke_test_social_publishing_gateway