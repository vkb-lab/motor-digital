# K-OS Social Strategy Generator v0.71B

Objetivo:
Criar estrategias sociais auditaveis em JSON para serem lidas pelo dashboard 71A.

Decisao anti-repeticao:
- Nao cria novo dashboard.
- Reutiliza o Social Ops Control Center 71A.
- Apenas adiciona geracao e registro de estrategias.

Comando:
python scripts\run_phase71b_social_strategy_generator.py --target hupmix --objective "crescer com teste controlado" --campaign hupmix-junho

Saidas:
- local_runtime/kos_social_ops/strategies/*.json
- local_runtime/kos_social_ops/latest_social_strategy.json

Garantias:
- Nao publica.
- Nao usa IA paga.
- Nao automatiza navegador logado.
- Parada Atlantida bloqueada.
- Hupmix-only nesta fase.
- Revisao humana obrigatoria.
