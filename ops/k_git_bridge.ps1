param(
    [ValidateSet("Status", "Pull", "Push", "Sync", "Log")]
    [string]$Action = "Status",

    [string]$CommitMessage = "chore: sync k-uni git bridge"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$RepoUrl = "https://github.com/vkb-lab/motor-digital.git"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git nao encontrado no sistema."
}

if (-not (Test-Path ".git")) {
    git init
}

$Remotes = git remote
if ($Remotes -contains "origin") {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

$Branch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($Branch)) {
    git checkout -B main
} elseif ($Branch -ne "main") {
    git checkout -B main
}

function Show-GitStatus {
    Write-Host "REPO:"
    Write-Host (Get-Location).Path
    Write-Host ""
    Write-Host "BRANCH:"
    git branch --show-current
    Write-Host ""
    Write-Host "REMOTE:"
    git remote -v
    Write-Host ""
    Write-Host "STATUS:"
    git status --short
}

function Invoke-SafePush {
    param([string]$Message)

    $SafePaths = @(
        ".github",
        "ops",
        "pages",
        "public_pages",
        "content_packs",
        "reports",
        "README.md",
        "K-ATLAS_CONTEXT.md",
        ".gitignore"
    )

    foreach ($Path in $SafePaths) {
        if (Test-Path $Path) {
            git add $Path
        }
    }

    git diff --cached --quiet
    $HasStaged = $LASTEXITCODE -ne 0

    if ($HasStaged) {
        git commit -m $Message
    } else {
        Write-Host "Sem alteracoes seguras para commit."
    }

    git push origin main
}

switch ($Action) {
    "Status" {
        Show-GitStatus
    }

    "Pull" {
        git pull --rebase origin main
        Show-GitStatus
    }

    "Push" {
        Invoke-SafePush -Message $CommitMessage
        Show-GitStatus
    }

    "Sync" {
        git pull --rebase origin main
        Invoke-SafePush -Message $CommitMessage
        Show-GitStatus
    }

    "Log" {
        git log --oneline -10
    }
}