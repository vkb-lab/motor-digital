# K-OS Fase 16 Public Asset URL Bridge

Objetivo:
Transformar a imagem gerada na Fase 15 em URL publica HTTPS para o Instagram.

Fluxo:
- localizar PNG em public/kos/assets/
- tentar deploy via vercel ou npx vercel
- salvar KOS_PUBLIC_BASE_URL em local_runtime/asset_runtime.env
- gerar image_url_for_instagram
- nao publicar no Instagram
