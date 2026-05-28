# K-Atlas OS - Cowork Prompt Generator

## Objetivo

Analisa o estado operacional do K-Atlas OS e sugere o proximo passo seguro para evolucao supervisionada.

## Leitura

- Lousa
- Cowork
- Dev Runner report
- AutoReporter module reports
- Self Evolution patch inbox
- Self Evolution patch approved

## Saida

- prioridade
- risco
- justificativa
- proximo passo correto
- proximo passo perigoso
- prompt sugerido para engenheiro IA

## Bloqueios

- nao executa comandos
- nao modifica codigo
- nao aprova patches
- nao aplica patches
- nao opera navegador
- nao acessa ChatGPT sozinho

## Uso

python .\k_atlas\cowork\prompt_generator.py generate

python .\k_atlas\cowork\prompt_generator.py status

python .\smoke_test_prompt_generator.py
