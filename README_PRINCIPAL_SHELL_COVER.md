# Checkpoint 123 - Principal Shell Cover

Capa operacional para o PowerShell principal do K-Atlas Local OS.

## Faz

- renderiza identidade visual do shell principal
- mostra estado dos modulos principais
- registra evento operacional
- gera relatorio JSON e Markdown
- cria pagina Streamlit de apoio
- cria atalho para abrir o shell principal

## Nao faz

- nao executa updates automaticamente
- nao controla mouse
- nao captura senha
- nao abre porta remota
- nao chama API externa

## Comando principal

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\k_shell_cover.ps1"

## Abrir nova janela com capa

powershell -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\open_principal_shell.ps1"
