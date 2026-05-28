# Closet Pilot

## Publico
Mulheres que querem organizar guarda-roupa, montar looks e reduzir indecisao na rotina.

## Problema
Muitas mulheres possuem um guarda-roupa com roupas suficientes, mas perdem tempo decidindo o que vestir, esquecem pecas que ja possuem e compram itens repetidos por falta de organizacao visual.

## Solucao
Um micro-SaaS simples para cadastrar pecas do guarda-roupa, classificar por categoria, cor, ocasiao e estacao, montar combinacoes basicas e planejar looks para trabalho, eventos, viagens e rotina.

## MVP
- Cadastro manual de pecas
- Categorias: blusa, calca, saia, vestido, casaco, sapato, acessorio
- Cores e ocasioes
- Status da peca: ativa, pouco usada, favorita
- Gerador simples de combinacoes por ocasiao
- Planejador semanal de looks
- Resumo do guarda-roupa por categoria e cor

## Nao fazer agora
- IA externa obrigatoria
- Upload automatico de imagem
- Marketplace
- Login multiusuario
- Pagamento
- Deploy cloud
- Recomendacao fashion complexa

## Primeiro teste
{
  "type": "streamlit_local_mvp",
  "goal": "Validar se a experiencia basica de cadastro e sugestao de looks funciona localmente.",
  "input_data": [
    "peca",
    "categoria",
    "cor",
    "ocasiao",
    "estacao",
    "favorita"
  ],
  "expected_output": [
    "lista de pecas cadastradas",
    "metricas simples do guarda-roupa",
    "sugestao basica de combinacao",
    "planejamento semanal manual"
  ]
}

## Criterios de sucesso
- App local abre sem erro
- Usuario consegue cadastrar pecas
- Usuario consegue visualizar pecas
- Sistema sugere pelo menos uma combinacao simples
- Smoke test valida estrutura do produto

## Riscos
- Escopo virar app de moda complexo cedo demais
- Adicionar IA visual antes de validar fluxo manual
- Criar login e pagamento antes do MVP
- Focar em design antes de validar utilidade

## Proximo passo correto
Gerar scaffold local Streamlit do Closet Pilot com dados JSON e smoke test.

## Proximo passo errado
Criar marketplace, login, pagamento ou IA visual antes do MVP local.
