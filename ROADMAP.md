# ROADMAP K-ATLAS

## Fase 1 — MVP Local
Status: concluída

- Painel local
- AI Brain
- Aprovação
- Landing
- GitHub
- Secrets locais

## Fase 2 — Supabase
Status: próxima

Objetivo:
Transformar arquivos locais em memória/fila multiaparelhos.

Criar:
- supabase/schema.sql
- k_atlas/integrations/supabase_client.py
- k_atlas/integrations/sync_to_supabase.py
- tabelas de prompts, planos, tarefas, aprovações, relatórios e projetos

## Fase 3 — Worker local

Objetivo:
K-Atlas Local ler tarefas do Supabase e executar no Windows.

Criar:
- k_atlas/worker.py
- fila pending/approved/running/done/error
- heartbeat do agente local

## Fase 4 — K-ND Web

Objetivo:
K-ND vira cockpit web multiaparelhos conectado ao Supabase.

Exibir:
- status do agente local
- fila de tarefas
- aprovações
- relatórios
- projetos
- últimas execuções

## Fase 5 — Integrações

- Gmail
- Instagram/Meta
- GitHub API
- automação de navegador
- publicação com confirmação
