# Checkpoint 32 - Creative Media Gateway

O Creative Media Gateway transforma brief em pacote criativo supervisionado.

## Fluxo

brief
-> prompt pack
-> asset plan
-> pacote criativo
-> aprovação humana
-> geração futura com vault
-> publishing gateway

## Status

planning_only

## Regras

- sem API externa por padrão
- sem publicação oficial
- sem browser automation
- sem token em texto puro
- geração real futura exige Credential Vault
- todo pacote exige aprovação humana

## Página

pages/13_K_Atlas_Creative_Media_Gateway.py

## Comando

python -m k_atlas.creative.media_gateway.export_package