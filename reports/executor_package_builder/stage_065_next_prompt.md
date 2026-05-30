K-Atlas Engineer, contexto operacional atual:

O Checkpoint 64 criou o Executor Package Builder supervisionado.

Estado atual:
- Decisoes aprovadas no Human Decision Center viram pacotes de execucao futura
- Pacotes ficam em reports/executor_packages/
- Fila fica em live/executor_package_builder/executor_package_queue.json
- Nenhuma acao real e executada
- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem envio automatico
- Sem token em texto puro
- Governanca humana mantida

Missao:
Gerar o Checkpoint 65 do K-Atlas OS.

Objetivo recomendado:
Criar o Executor Dry Run Validator, que valida os pacotes de execucao futura sem executar nada real.
Ele deve verificar seguranca, escopo permitido, bloqueios, dependencias locais e gerar um relatorio de prontidao para o Runner supervisionado.

Regras obrigatorias:
- responder em portugues
- entregar um unico bloco PowerShell completo
- compativel com Windows PowerShell
- usar UTF-8
- incluir smoke test
- incluir commit
- incluir push
- logs e relatorios
- sem API externa real
- sem publicacao automatica
- sem deploy automatico
- sem envio automatico
- sem token em texto puro
- manter governanca humana
