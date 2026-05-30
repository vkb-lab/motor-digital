param(
    [Parameter(Mandatory=$true)]
    [int]$Start,

    [Parameter(Mandatory=$true)]
    [int]$End,

    [Parameter(Mandatory=$true)]
    [string]$BatchName,

    [Parameter(Mandatory=$true)]
    [string]$Names,

    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    throw "Python virtualenv nao encontrado."
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

$Items = $Names.Split("|") | ForEach-Object { $_.Trim() } | Where-Object { $_ }

if ($Items.Count -ne (($End - $Start) + 1)) {
    throw "Quantidade de nomes nao bate com intervalo do batch."
}

$Spec = [ordered]@{
    start = $Start
    end = $End
    batch_name = $BatchName
    commit_message = $CommitMessage
    items = $Items
}

$Spec | ConvertTo-Json -Depth 20 | Set-Content -Path ".k_atlas_batch_factory_spec.json" -Encoding UTF8

& $Python ".\ops\k_batch_factory.py"

if ($LASTEXITCODE -ne 0) {
    throw "Batch Factory falhou ao gerar arquivos."
}

for ($i = 0; $i -lt $Items.Count; $i++) {
    $Name = $Items[$i].ToLower()
    $Slug = ($Name -replace "[^a-z0-9]+", "_").Trim("_")

    & $Python -m "k_atlas.core.$Slug.smoke_test_$Slug"

    if ($LASTEXITCODE -ne 0) {
        throw "Smoke test falhou em $Slug"
    }
}

if (Test-Path ".\ops\log_cowork_event.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\log_cowork_event.ps1" -Title "Batch $Start-$End executado" -Details "$BatchName gerado pelo Batch Factory Local." -EventType "batch_factory"
}

git add k_atlas/core
git add pages
git add ops
git add README_BATCH_*

git diff --cached --quiet
$HasStaged = $LASTEXITCODE -ne 0

if ($HasStaged) {
    if (-not $CommitMessage) {
        $CommitMessage = "feat: add batch $Start-$End $BatchName"
    }

    git commit -m $CommitMessage
    git push origin main
} else {
    Write-Host "Nada novo para commitar."
}

Remove-Item ".k_atlas_batch_factory_spec.json" -Force -ErrorAction SilentlyContinue

git status --short

Write-Host "BATCH $Start-$End CONCLUIDO"
Write-Host "$BatchName OPERACIONAL"