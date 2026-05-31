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
