# BRICS Paraguay Autos

## Objetivo
Criar marketplace vertical de automoveis no Paraguai com cadastro assistido por camera e IA, mantendo revisao humana obrigatoria antes de publicar.

## Problema
Publicar anuncio de veiculo costuma exigir muitos campos manuais. Isso reduz conversao, gera anuncios incompletos e dificulta padronizacao.

## Solucao
O usuario fotografa o veiculo, a IA sugere dados do anuncio e o vendedor revisa antes de publicar.

## MVP
- captura de foto por camera ou upload
- cadastro de anuncio de veiculo
- IA assistida para sugerir titulo e descricao
- IA assistida para sugerir cor, categoria e estado visual aparente
- campos manuais obrigatorios para ano, preco, cidade, telefone e documentacao informada
- revisao humana obrigatoria antes de publicar
- dashboard administrativo inicial
- idiomas portugues e espanhol

## IA assistida
Modo: assistive_only
Revisao humana obrigatoria: sim

## Dashboard v1
- anuncios totais
- anuncios pendentes de revisao
- anuncios publicados
- anuncios incompletos
- veiculos por cidade
- veiculos por faixa de preco
- leads por anuncio
- alertas de moderacao futura
- anuncios com sugestao de IA nao revisada

## Governanca
{
  "creative_brief_required": true,
  "specialist_council_required": true,
  "legal_review_required_before_real_launch": true,
  "tax_review_required_before_monetization": true,
  "human_approval_required_before_publish": true,
  "no_copy_policy": "Nao copiar OLX, identidade visual, marca, layout, codigo ou assets. Usar apenas referencia de categoria: classificados."
}

## Nao fazer agora
- pagamento
- login completo
- deploy cloud
- publicacao automatica
- validacao juridica automatica
- marketplace completo multi-categoria
- clone visual de concorrente

## Proximo passo correto
Criar scaffold MVP local do BRICS Paraguay Autos com upload/camera simulada, IA mock assistida, revisao humana e dashboard inicial.

## Proximo passo errado
Criar marketplace completo, copiar OLX, adicionar pagamento, login ou deploy antes do MVP supervisionado.
