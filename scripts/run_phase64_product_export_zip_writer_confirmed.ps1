param(
  [Parameter(Mandatory=$true)]
  [string]$ProductSlug,

  [Parameter(Mandatory=$true)]
  [string]$Confirmation
)

$ErrorActionPreference="Stop"

Set-Location "C:\Users\oi\Desktop\motor-digital"
$env:PYTHONPATH="C:\Users\oi\Desktop\motor-digital"

if($Confirmation -ne "YES_CREATE_PRODUCT_EXPORT_ZIP_LOCAL_ONLY"){
  Write-Host "[KOS] Confirmacao invalida. Zip bloqueado."
  throw "Confirmacao exigida: YES_CREATE_PRODUCT_EXPORT_ZIP_LOCAL_ONLY"
}

python -c "import json; from k_atlas.product_factory.product_export_zip_writer_gate import create_product_export_zip; print(json.dumps(create_product_export_zip(product_slug='$ProductSlug', confirmation='$Confirmation'), ensure_ascii=False, indent=2))"