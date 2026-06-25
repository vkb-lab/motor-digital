# KOS Origin Core Registry Plan

Timestamp: 2026-06-25 18:21:59 America/Sao_Paulo
Patch: K-OS Origin Core Registry v1
Base: `reports/KOS_ORIGIN_TO_DESTINATION_DOSSIER_20260625_155037.md`

## Base usada

Este plano usa como fonte de verdade o dossie historico `KOS_ORIGIN_TO_DESTINATION_DOSSIER_20260625_155037.md`.

O dossie confirmou:

- primeiro commit: `eb0db4e`;
- primeiro titulo: `Criar app.py com interface Streamlit - Torre de Controle IA`;
- origem como Torre de Controle IA;
- evolucao para K-Atlas, K-OS, K-Uni, Operator Chat, Gmail, Google Toolbelt, Brain Provider e Render read-only;
- destino como K-OS privado, soberano, local-first, com ferramentas externas subordinadas.

## O que foi registrado

Arquivos criados:

- `memory/kos_governance/KOS_ORIGIN_CORE_REGISTRY.json`
- `memory/kos_governance/KOS_UNICORN_BUILDER_OS_DOCTRINE_V1.md`
- `memory/kos_skills/KOS_SKILL_ORIGIN_TO_DESTINATION_REASONING_V1.md`
- `scripts/run_kos_origin_core_status.py`
- `tests/test_kos_origin_core_registry.py`

## Nucleo

O registry registra o ciclo operacional:

1. `human_intent`
2. `memory_context`
3. `routing`
4. `risk_assessment`
5. `safe_execution_or_human_gate`
6. `evidence`
7. `reusable_learning`

Home oficial:

```text
app.py
```

Cloud read-only:

```text
app_render.py
```

## Origem

O K-OS nasce do commit:

```text
eb0db4e Criar app.py com interface Streamlit - Torre de Controle IA
```

A origem operacional consolidada veio da transicao:

```text
Torre de Controle IA -> Motor Digital -> K-Atlas Local -> K-OS
```

## Destino

Destino registrado:

- K-OS privado e soberano de Rogger;
- cockpit local enxuto;
- Render como observatorio read-only/mobile;
- ferramentas externas como bracos, nao substitutas;
- produtos e startups como saidas;
- cada projeto como materia-prima de aprendizado reutilizavel.

## Legado a ocultar

O registry marca como legado a ocultar da navegacao principal:

- K-Atlas numbered mass pages;
- K-Uni Marketplace pages;
- old command centers;
- duplicated gates;
- granular K-OS core pages 915-976;
- exposed GitHub admin/vault/publish/live/deploy pages.

Nada foi deletado.

## Status

Comandos executados:

```powershell
python -m py_compile scripts/run_kos_origin_core_status.py
python -m pytest tests/test_kos_origin_core_registry.py -q
python scripts/run_kos_origin_core_status.py --mode status
```

Resultado dos testes:

```text
......                                                                   [100%]
```

Resumo do status:

```json
{
  "status": "KOS_ORIGIN_CORE_STATUS_READY",
  "registry_status": "KOS_ORIGIN_CORE_REGISTRY_ACTIVE",
  "official_home_exists": true,
  "cloud_readonly_exists": true,
  "core_files_found_count": 11,
  "core_files_missing_count": 0,
  "next_patch_recommended": "K-OS Custom Navigation v1"
}
```

## Proximo patch

Proximo patch recomendado:

```text
K-OS Custom Navigation v1
```

Objetivo:

- fazer a home e a navegacao lerem o Origin Core Registry;
- expor somente o nucleo oficial;
- manter legado acessivel por diagnostico/busca;
- nao deletar paginas;
- impedir que paginas perigosas fiquem na frente do operador.

