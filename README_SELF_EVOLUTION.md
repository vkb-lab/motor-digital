# K-Atlas OS - Self Evolution Layer

Camada inicial de autoevolucao supervisionada do K-Atlas OS.

## Regra principal

Esta camada NAO altera codigo automaticamente.

## Objetivos

- registrar gargalos
- criar pedidos de melhoria
- gerar propostas de patch
- calcular risco basico
- gerar diff
- exigir approval humano
- preparar snapshot
- preparar rollback

## Estrutura

k_atlas/self_evolution/
- ask_engineer.py
- patch_engine.py
- diff_viewer.py
- risk_analyzer.py
- approval_gate.py
- patch_requests/
- patch_inbox/
- patch_approved/
- patch_rejected/
- snapshots/
- rollback/

## Politica

- autoapproval: bloqueado
- auto apply: bloqueado
- alteracao destrutiva: bloqueada
- core: exige approval especial
- internet: nao acessa sozinho
- memoria critica: nao sobrescreve

## Proximo passo

Integrar ao dev_runner em modo teste.
Depois integrar ao cockpit em modo read-only.
