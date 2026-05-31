# K-OS Context API Catalog

- Status: endpoint_catalog_generated
- Bind address: 127.0.0.1
- Default port: 8583
- Local only: True
- Raw payload return allowed: False

## Endpoints

- GET /health - Retornar status local da API.
- GET /catalog - Listar endpoints e filtros permitidos.
- GET /retrieve - Recuperar eventos e contexto sanitizado.
- GET /domains - Listar domínios disponíveis no índice.
- GET /events - Recuperar apenas eventos sanitizados.
- GET /context - Recuperar apenas contexto sanitizado.