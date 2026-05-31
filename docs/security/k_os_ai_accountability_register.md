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
