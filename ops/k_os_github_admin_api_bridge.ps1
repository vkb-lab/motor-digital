param(
    [ValidateSet("Doctor", "EnablePagesRoot", "CheckPages", "MakePublicAndEnablePages", "OpenGitHub")]
    [string]$Action = "Doctor",

    [switch]$ConfirmPublic
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Owner = "vkb-lab"
$Repo = "motor-digital"
$Full = "$Owner/$Repo"
$PublicUrl = "https://vkb-lab.github.io/motor-digital/"
$RepoUrl = "https://github.com/vkb-lab/motor-digital"

cd "C:\Users\oi\Desktop\motor-digital"

function Assert-Gh {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI nao encontrado. Instale com: winget install --id GitHub.cli -e --source winget"
    }

    gh auth status | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI nao autenticado. Rode: gh auth login"
    }
}

function Invoke-GhJson {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null
    )

    if ($null -eq $Body) {
        gh api --method $Method -H "Accept: application/vnd.github+json" $Endpoint
        return
    }

    $Temp = [System.IO.Path]::GetTempFileName()
    $Json = $Body | ConvertTo-Json -Depth 20
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Temp, $Json, $Utf8NoBom)

    try {
        gh api --method $Method -H "Accept: application/vnd.github+json" $Endpoint --input $Temp
    } finally {
        Remove-Item $Temp -Force -ErrorAction SilentlyContinue
    }
}

function Get-RepoState {
    Write-Host ""
    Write-Host "REPO STATE"
    Write-Host "----------"
    gh repo view $Full --json name,visibility,isPrivate,defaultBranchRef,url
}

function Get-PagesState {
    Write-Host ""
    Write-Host "PAGES STATE"
    Write-Host "-----------"

    gh api "/repos/$Full/pages" 2>$null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "GitHub Pages ainda nao existe ou nao esta acessivel pela API."
    }
}

function Enable-PagesRoot {
    Write-Host "Ativando GitHub Pages em main /root..."

    $Body = @{
        source = @{
            branch = "main"
            path = "/"
        }
    }

    gh api "/repos/$Full/pages" 1>$null 2>$null
    $Exists = $LASTEXITCODE -eq 0

    if ($Exists) {
        Invoke-GhJson -Method "PUT" -Endpoint "/repos/$Full/pages" -Body $Body
        Write-Host "Pages atualizado para main /root."
    } else {
        Invoke-GhJson -Method "POST" -Endpoint "/repos/$Full/pages" -Body $Body
        Write-Host "Pages criado em main /root."
    }
}

function Make-RepoPublic {
    if (-not $ConfirmPublic) {
        throw "Acao bloqueada. Para tornar publico, rode com -ConfirmPublic."
    }

    Write-Host "Alterando visibilidade do repositorio para PUBLIC..."
    gh api --method PATCH "/repos/$Full" -f visibility=public
    Write-Host "Repositorio alterado para publico."
}

function Write-Report {
    param([string]$Status)

    $ReportPath = "reports\system\k_os_github_admin_api_bridge_status.json"

    $Report = [ordered]@{
        ok = $true
        module = "k_os_github_admin_api_bridge"
        action = $Action
        status = $Status
        repo = $Full
        public_url = $PublicUrl
        external_publish_enabled = $false
        manual_approval_required = $true
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
    }

    $Report | ConvertTo-Json -Depth 10 | Set-Content -Path $ReportPath -Encoding UTF8
    Write-Host "Relatorio:" $ReportPath
}

Assert-Gh

switch ($Action) {
    "Doctor" {
        Get-RepoState
        Get-PagesState
        Write-Report -Status "doctor_completed"
    }

    "CheckPages" {
        Get-PagesState
        Write-Report -Status "pages_checked"
    }

    "EnablePagesRoot" {
        Enable-PagesRoot
        Get-PagesState
        Write-Report -Status "pages_root_enabled"
    }

    "MakePublicAndEnablePages" {
        Make-RepoPublic
        Enable-PagesRoot
        Get-RepoState
        Get-PagesState
        Write-Report -Status "repo_public_and_pages_enabled"
    }

    "OpenGitHub" {
        Start-Process "$RepoUrl/settings/pages"
        Start-Process "$RepoUrl/actions"
        Start-Process $PublicUrl
        Write-Report -Status "github_opened"
    }
}