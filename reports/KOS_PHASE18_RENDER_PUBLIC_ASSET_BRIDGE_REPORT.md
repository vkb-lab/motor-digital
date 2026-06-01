# K-OS FASE 18 - RENDER PUBLIC ASSET BRIDGE

Status: PRONTO FASE 18

## Decisao

A plataforma correta para este projeto e Render.

Vercel foi descartado nesta etapa.

## Servicos Render definidos

1. k-atlas-os
   - Web Service Python
   - Streamlit
   - startCommand usando app.py
   - porta dinamica via $PORT

2. k-atlas-assets
   - Static Site
   - publica a pasta public/
   - entrega imagens em /kos/assets/

## URL esperada da imagem

https://k-atlas-assets.onrender.com/kos/assets/parada_atlantida_campanha_lancamento_parada_atlantida.png

## Seguran?a

- Nao publica Instagram.
- Nao exp?e token.
- Nao altera local_runtime/ig_runtime.env.
- KOS_EXTERNAL_PUBLISH_ENABLED=false no Render.

## Proximo passo

Abrir Render, criar Blueprint pelo repositorio GitHub e confirmar os dois servicos.
