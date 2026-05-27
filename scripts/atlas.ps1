param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Pedido
)

Set-Location "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\activate") {
    . .\venv\Scripts\activate
}

$texto = $Pedido -join " "

if ([string]::IsNullOrWhiteSpace($texto)) {
    Write-Host ""
    Write-Host "K-Atlas Local" -ForegroundColor Cyan
    Write-Host "Uso:"
    Write-Host '  .\scripts\atlas.ps1 "seu pedido aqui"'
    Write-Host ""
    Write-Host "Exemplos:"
    Write-Host '  .\scripts\atlas.ps1 "crie uma landing page para Parada Atlântida vender chopp grátis"'
    Write-Host '  .\scripts\atlas.ps1 "analise minha área de trabalho"'
    Write-Host ""
    exit
}

python -m k_atlas.run "$texto"
