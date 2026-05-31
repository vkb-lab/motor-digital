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
