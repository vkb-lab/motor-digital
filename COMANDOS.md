# COMANDOS K-ATLAS LOCAL

## Entrar no projeto

cd C:\Users\oi\Desktop\motor-digital
.\venv\Scripts\activate

## Atualizar do GitHub

git pull origin main

## Ver status

python -m k_atlas.status

## Rodar painel

streamlit run local_dashboard.py

## Enviar pedido pelo terminal

.\scripts\atlas.ps1 "seu pedido"

## Aprovar próxima ação

.\scripts\aprovar.ps1

## Salvar no GitHub

git add .
git commit -m "mensagem"
git push origin main

## Abrir última landing

Start-Process (Get-ChildItem k_atlas\workspace -Recurse -Filter index.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
