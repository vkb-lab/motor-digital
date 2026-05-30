# Checkpoint 38 - SaaS Factory Workflow Real

Cria um MVP SaaS real de forma supervisionada.

## Fluxo

brief -> validação -> spec -> MVP Streamlit -> compile check -> deploy_plan -> relatório

## Saídas

- k_atlas/saas_factory/products/<produto>
- reports/saas_factory/workflows/latest_saas_factory_workflow.json

## Regras

- Sem deploy automático.
- Sem API externa.
- Sem publicação oficial.
- Sem token em texto puro.
- Revisão humana obrigatória.

## Página

pages/19_K_Atlas_SaaS_Factory_Workflow.py

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_saas_factory_workflow.ps1"
