# K-OS Roadmap Planner and Release Notes Core

Checkpoint 035.

Objetivo:

- organizar roadmap interno
- planejar releases
- ligar features a versões
- gerar notas de release
- separar release interna de release pública
- bloquear promessa externa sem aprovação
- preparar evolução SaaS governada

## Regra central

Roadmap Planner é local.

Ele não:

- publica release automaticamente
- publica roadmap externamente
- promete feature ao cliente
- comita roadmap bruto
- marca release pública sem revisão
- apaga logs de auditoria

## Dados reais

O registro bruto fica em:

local_secrets/k_os_roadmap/roadmap_release_registry.json

Esse arquivo não vai para o GitHub.

Os relatórios em reports/roadmap são sanitizados.

## Antes de release pública

- release existe
- features vinculadas revisadas
- Product Owner revisou
- QA ou operador revisou
- comercial revisou se customer-facing
- segurança revisou se aplicável
- jurídico revisou se aplicável
- notas de release revisadas
- aprovação humana registrada

## Próximo checkpoint

036 - K-Analytics and Executive Metrics Core