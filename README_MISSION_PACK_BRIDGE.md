# Checkpoint 75 - Mission Pack Bridge

Converte mission packs gerados pelo Checkpoint 74 em local missions compativeis com o Local Mission Installer do Checkpoint 73.

## Fluxo

Mission Pack Generator -> Mission Pack Bridge -> Local Mission Installer

## Faz

- le live/mission_pack_generator/latest_mission_pack.json
- valida o mission pack
- converte para schema k_atlas.local_mission.v1
- valida com a policy do Local Mission Installer
- gera arquivo .kmission.json
- gera relatorio JSON e Markdown
- cria pagina Streamlit

## Nao faz

- nao instala automaticamente
- nao executa comandos
- nao chama API externa
- nao publica
- nao envia mensagens
- nao faz deploy

## Saidas

- live/mission_pack_bridge/latest_local_mission.kmission.json
- live/mission_pack_bridge/generated_local_missions/

## Comando

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\bridge_latest_mission_pack.ps1"
