$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Project = "C:\Users\oi\Desktop\motor-digital"
$Downloads = Join-Path $env:USERPROFILE "Downloads"

cd $Project

$Candidates = @()

if (Test-Path $Downloads) {
    $Candidates += Get-ChildItem -Path $Downloads -Filter "K_ATLAS_*.ps1" -File -ErrorAction SilentlyContinue
}

$Candidates += Get-ChildItem -Path $Project -Filter "K_ATLAS_*.ps1" -File -ErrorAction SilentlyContinue

$Latest = $Candidates |
    Where-Object { $_.Name -match "^(K_ATLAS_(CHECKPOINT|BATCH|FIX)_.+\.ps1)$" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Latest) {
    Write-Host "Nenhum instalador K_ATLAS novo encontrado."
    exit 0
}

$Destination = Join-Path $Project $Latest.Name

if ($Latest.FullName -ne $Destination) {
    Copy-Item -Path $Latest.FullName -Destination $Destination -Force
}

Write-Host "Executando instalador mais recente:"
Write-Host $Latest.Name
Write-Host ""

powershell -ExecutionPolicy Bypass -File $Destination