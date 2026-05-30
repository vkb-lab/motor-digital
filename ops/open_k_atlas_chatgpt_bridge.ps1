Stop = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$ChatUrl = "https://chatgpt.com/g/g-6a1835a4bd9c8191b314ede2fffc8923-k-atlas-engineer/c/6a19912f-65e8-83e9-9360-cc453aa5a212"

$Prompt = Get-Content "memory\chatgpt_bridge\next5_prompt.md" -Raw -Encoding UTF8
Set-Clipboard -Value $Prompt

Start-Process $ChatUrl

Write-Host "ChatGPT K-Atlas aberto."
Write-Host "Prompt operacional copiado para a area de transferencia."
Write-Host "Cole no chat e envie."
