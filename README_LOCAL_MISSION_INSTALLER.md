# Checkpoint 73 - Local Mission Installer

Instalador local declarativo para reduzir blocos gigantes copiados do chat para o PowerShell.

## Objetivo

Transformar o chat em arquiteto e o K-Atlas local em executor governado.

## Faz

- cria missoes locais declarativas
- importa arquivos `.kmission.json`
- valida schema, caminhos, hashes e conteudo
- bloqueia shell, API externa, deploy, publish e envio automatico
- executa dry-run
- exige aprovacao humana
- instala apenas passos seguros `write_file` e `append_file`
- cria backup antes de sobrescrever
- gera manifesto e relatorios

## Nao faz

- nao executa PowerShell arbitrario
- nao executa Python arbitrario
- nao chama API externa
- nao publica
- nao envia mensagem
- nao faz deploy
- nao move mouse
- nao automatiza navegador

## Pagina

pages/73_K_Atlas_Local_Mission_Installer.py

## Demo

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\run_local_mission_installer_demo.ps1"

## Uso futuro

1. Salvar arquivo `.kmission.json` no projeto.
2. Rodar `ops/install_local_mission.ps1 -MissionPath <arquivo>`.
3. Revisar dry-run.
4. Aprovar manualmente.
5. Instalar com `-Approve -Install`.
