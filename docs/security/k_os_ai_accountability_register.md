# K-OS AI Accountability Register

Este documento inicia o registro de responsabilidade das IAs do K-OS.

## Princípio

Toda IA ou agente precisa ter:

- nome
- função
- dono humano
- permissão
- limites
- risco
- approval gate
- evidência gerada

## Registro inicial

| IA / Agente | Função | Dono humano | Pode executar? | Pode publicar? | Pode enviar mensagem? | Approval gate | Evidência |
|---|---|---|---:|---:|---:|---|---|
| K-Atlas Engineer | Arquitetura e programação supervisionada | Operador K-OS | Não diretamente | Não | Não | Sim | Chat + commits + relatórios |
| K-Uni Cockpit | Operação visual local | Operador K-OS | Apenas ações locais aprovadas | Não | Não | Sim | Streamlit + reports |
| Marketplace IA Agent | Diagnóstico e proposta local | Operador K-OS | Não | Não | Não | Sim | live/ + reports |
| Git Bridge | Commit/push seguro | Operador K-OS | Sim, limitado | Não | Não | Sim | git log + reports |
| Security Firewall | Bloqueio de risco antes do commit | Operador K-OS | Sim, bloqueio local | Não | Não | Automático + humano | reports/security |

## Campos futuros obrigatórios

- classificação de risco
- finalidade permitida
- dados acessados
- integrações permitidas
- logs obrigatórios
- política de retenção
- humano responsável
- conselho de revisão
| K-Schema Guard | Validação estrutural de JSON operacional | Operador K-OS | Sim, validação local | Não | Não | Automático + humano | reports/schema |

| K-OS Agent Permission Matrix | Define permissões, limites e responsabilidade dos agentes | Operador K-OS | Sim, validação local | Não | Não | Security Council + AI Accountability Council | reports/governance |

| K-OS Vault Guard | Cofre local de chaves e política de acesso controlado | Operador K-OS | Sim, auditoria local | Não | Não | Security Council + Human Approval | reports/vault |

| K-OS Audit Evidence Pack | Consolida evidências, controles, gaps e readiness de auditoria | Operador K-OS | Sim, relatório local | Não | Não | Security Council + AI Accountability Council | reports/audit |

| K-OS Mission Control 2.0 | Consolida status, risco, gates e próximos passos da nave | Operador K-OS | Sim, leitura local | Não | Não | Human Approval + Security Council | reports/mission_control |

| K-OS AI Risk Classifier | Classifica risco, exige gates e bloqueia ações perigosas | Operador K-OS | Sim, validação local | Não | Não | Human Approval + Security Council | reports/risk |
| K-OS License Gate | Controla ativação comercial, assinatura e revogação segura de agentes | Operador K-OS | Sim, local | Não | Não | License Gate + Security Council | reports/license |

| K-OS External API Sandbox | Simula conectores externos sem chamada real, com risco, licença e vault | Operador K-OS | Sim, sandbox local | Não | Não | Human Approval + Security Council + License Gate | reports/external_sandbox |

| K-OS Enterprise Readiness Report | Consolida evidencias enterprise, maturidade, gaps e pacote de due diligence | Operador K-OS | Sim, leitura local | Não | Não | Human Approval + Security Council | reports/enterprise |

| K-OS Legal Commercial License Templates | Gera templates comerciais para licenca, assinatura, SLA, uso aceitavel e revogacao segura | Operador K-OS | Sim, local | Não | Não | Human Approval + Legal Review + Security Council | reports/legal |

| K-OS Billing and Subscription Ledger | Registra assinaturas, status de pagamento, vencimentos e bloqueios comerciais seguros | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + License Gate | reports/billing |

| K-OS Customer Registry and CRM Core | Registra clientes, leads, status comercial, vinculos e historico CRM sanitizado | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + Privacy Review | reports/crm |

| K-OS Sales Pipeline and Deal Desk | Organiza oportunidades, funil, valores, propostas e aprovacoes comerciais | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + Legal Review | reports/sales |

| K-OS Proposal Factory and Quote Builder | Gera propostas e orcamentos locais com approval gate antes de envio manual | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + Legal Review | reports/proposals |

| K-OS Onboarding and Activation Gate | Valida CRM, assinatura, licença, deal, proposta, risco e permissões antes de ativação manual | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + Security Review | reports/onboarding |

| K-OS Customer Success and Delivery Tracker | Acompanha entregas, tarefas, saúde do cliente, riscos e próximas ações | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Customer Success Review + Commercial Review | reports/customer_success |

| K-OS Support Desk and Ticketing Core | Registra tickets, prioridades, SLA operacional, triagem e escalonamento de suporte | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Support Review + Incident Review | reports/support |

| K-OS Knowledge Base and Support Playbooks | Cria artigos, playbooks, templates internos e vinculos com tickets recorrentes | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Support Review + Security/Legal Review | reports/knowledge_base |

| K-OS Product Feedback and Feature Request Core | Registra feedback, pedidos de melhoria, features, impacto, esforço, backlog e candidatos de roadmap | Product Owner K-OS | Sim, local sanitizado | Não | Não | Human Approval + Product Review + Commercial/Security/Legal Review | reports/product_feedback |

| K-OS Roadmap Planner and Release Notes Core | Organiza roadmap interno, releases, features por versao e notas de release com bloqueio de publicacao externa | Product Owner K-OS | Sim, local sanitizado | Não | Não | Human Approval + Product Review + QA/Security/Legal Review | reports/roadmap |

| K-OS Analytics and Executive Metrics Core | Consolida métricas executivas sanitizadas, KPIs, saúde operacional e score de controles | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Commercial Review + Security Review | reports/analytics |

| K-OS Executive Cockpit Consolidation Layer | Consolida painéis, módulos, navegação, métricas executivas e health operacional em cockpit central | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Security Review + Commercial Review | reports/cockpit |

| K-OS Command Center Action Router | Roteia ações controladas por allowlist, dry-run, approval gate e auditoria | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Action Allowlist + Security Gate | reports/command_center |

| K-OS Agent Orchestration Queue Core | Cria fila governada de tarefas para agentes com permissão, dry-run, dispatch via Command Center e auditoria | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Agent Permission Matrix + Command Center Gate | reports/agent_queue |

| K-OS Agent Runtime Supervisor Core | Supervisiona runtime de agentes, heartbeat, watchdog, stale agents, bloqueios preventivos e auditoria | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Agent Queue + Permission Matrix + Watchdog | reports/agent_runtime |

| K-OS Agent Execution Ledger and Replay Core | Registra ledger auditavel de execucoes, hashes, evidencias e replay controlado via Command Center | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Command Center Gate + Evidence Hash | reports/agent_ledger |

| K-OS Memory Event Bus and Context Index Core | Indexa eventos operacionais, contexto sanitizado, buscas locais e trilha de memoria evolutiva | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Security Review + Payload Hashing | reports/memory_bus |

| K-OS Context Retrieval API Core | API local para recuperar contexto sanitizado da memoria indexada e servir agentes/cockpit | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Local API + Payload Hashing | reports/context_api |

| K-OS Agent Prompt Assembly and Execution Plan Core | Monta prompt operacional sanitizado e plano de execução governado para agentes | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Context Packet + Secret Scan + Dry Run Gate | reports/prompt_assembly |

| K-OS Agent Dry Run Executor Core | Executa plano de agente em dry-run, simula passos, registra evidência e bloqueia efeitos reais | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Prompt Package + Execution Plan + Dry Run Evidence | reports/dry_run_executor |

| K-OS Agent Real Execution Approval Gate Core | Aprova, bloqueia ou revoga execução real de agentes após dry-run validado e decisão humana | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Dry Run Evidence + Local Authorization Hash | reports/real_execution_gate |

| K-OS Agent Safe Execution Router Core | Roteia execução aprovada para executor allowlisted com validação de aprovação, dry-run, permissão e allowlist | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Local Authorization Hash + Allowlist + Router Gate | reports/safe_execution_router |

| K-OS Agent Allowlisted Action Executor Core | Executa somente ações internas permitidas por allowlist com rota segura validada e evidência antes/depois | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Safe Route + Allowlist + Evidence Hash | reports/allowlisted_action_executor |

| K-OS Agent Execution Result Ledger Core | Registra resultados de execução allowlisted com hashes, cadeia auditável e referências sanitizadas | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Execution Evidence + Append-Only Ledger | reports/execution_result_ledger |

| K-OS Agent Replay and Forensics Viewer Core | Reconstrói timeline e bundle forensics de execução governada sem replay ativo ou payload bruto | Operador K-OS | Sim, local sanitizado | Não | Não | Read-Only Viewer + Ledger Hash + Source Verification | reports/replay_forensics |

| K-OS Agent Incident Lockdown and Quarantine Core | Bloqueia agentes/execuções em incidente, cria quarentena local e preserva evidências sem apagar dados | Operador K-OS | Sim, local sanitizado | Não | Não | Human Review + Forensics Bundle + Quarantine Hash | reports/incident_lockdown |

| K-OS Agent Rollback Preparation Core | Prepara plano de rollback seguro a partir de incidente/quarentena sem executar mudanças ou apagar dados | Operador K-OS | Sim, local sanitizado | Não | Não | Human Approval + Incident Lockdown + Forensics + Ledger | reports/rollback_preparation |

| K-OS Agent Rollback Approval and Release Gate Core | Registra aprovação, bloqueio ou revogação para rollback futuro sem executar mudanças | Operador K-OS | Sim, local sanitizado | Não | Não | Human Operator + Release Hash + No Rollback Execution | reports/rollback_release_gate |

| K-OS Agent Rollback Dry Run Simulator Core | Simula rollback sem executar mudanças, respeitando gate de release e registrando evidência auditável | Operador K-OS | Sim, local sanitizado | Não | Não | Dry Run + Release Gate + No File Change + No Data Delete | reports/rollback_dry_run |
