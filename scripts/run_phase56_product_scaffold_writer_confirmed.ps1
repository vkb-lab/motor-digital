$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

Write-Host "[KOS] Product Scaffold Writer Local"
Write-Host "[KOS] Esta acao cria arquivos locais em products/<slug>/."
Write-Host "[KOS] Nao faz deploy, nao usa IA paga, nao publica."

$Confirm=(Read-Host "Para criar scaffold local, digite exatamente YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY").Trim()

if($Confirm -ne "YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY"){
  Write-Host "[KOS] Confirmacao incorreta. Rodando apenas dry-run."
  $env:KOS_PRODUCT_SCAFFOLD_EXECUTE="false"
  $env:KOS_PRODUCT_SCAFFOLD_CONFIRMATION=$Confirm
  python scripts\run_phase56_product_scaffold_writer.py
  exit 0
}

$env:KOS_PRODUCT_SCAFFOLD_EXECUTE="true"
$env:KOS_PRODUCT_SCAFFOLD_CONFIRMATION=$Confirm

python scripts\run_phase56_product_scaffold_writer.py