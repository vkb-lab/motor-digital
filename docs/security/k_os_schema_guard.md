# K-OS Schema Guard

## Checkpoint 016

Objetivo:

- validar JSON antes de uso operacional
- impedir que saída quebrada de IA trave Approval Gates
- proteger diagnósticos, propostas, leads e decisões
- gerar evidência para auditoria
- preparar Structured Outputs e Pydantic no futuro

## Schemas iniciais

| Schema | Uso |
|---|---|
| lead_v1 | leads capturados localmente |
| public_capture_v1 | captura pública controlada |
| diagnostic_v1 | diagnóstico com recomendações |
| proposal_v1 | proposta comercial |
| gate_decision_v1 | aprovação, reprovação ou pendência |
| instagram_posts_v1 | campanha em posts |
| generic_json_v1 | JSON genérico válido |

## Regra de segurança

Campos como external_send_enabled precisam ser false em objetos operacionais.

## Política

- sem API externa
- sem publicação automática
- sem envio automático
- aprovação humana obrigatória
- relatório gerado em reports/schema/
- eventos locais em memory/schema_guard/