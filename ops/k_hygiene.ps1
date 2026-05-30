param(
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$Now = Get-Date
$ReportPath = "reports\k_uni_hygiene\latest_hygiene_report.json"

$ProtectedRoots = @(
    ".git",
    "k_atlas",
    "agents",
    "pages",
    "ops",
    "README.md",
    "K-ATLAS_CONTEXT.md",
    "memory\manual_apply_executor",
    "memory\manual_apply_rollback_executor",
    "memory\cowork_pilot_studio",
    "memory\k_uni_runtime"
)

$Targets = @()

$Patterns = @(
    "__pycache__",
    ".pytest_cache"
)

foreach ($Pattern in $Patterns) {
    $Targets += Get-ChildItem -Path "." -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq $Pattern }
}

$Targets += Get-ChildItem -Path "." -File -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match "\.pyc$" -or
        $_.Name -match "^K_ATLAS_.*\.ps1$" -or
        $_.Name -match "^K_ATLAS_.*INSTALL.*\.ps1$" -or
        $_.Name -match "^K_ATLAS_.*BATCH.*\.ps1$"
    }

$Targets += Get-ChildItem -Path "." -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match "^\.mission_pipeline_.*" -or
        $_.Name -match "^\.batch_.*"
    }

$Targets += Get-ChildItem -Path "memory\auto_update_watcher\processed_installers" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $Now.AddDays(-2) }

$Plan = @()

foreach ($Target in $Targets) {
    $Full = $Target.FullName
    $Relative = Resolve-Path -Path $Full -Relative -ErrorAction SilentlyContinue

    $Blocked = $false

    foreach ($Protected in $ProtectedRoots) {
        if ($Relative -like ".\$Protected*" -and $Protected -notlike "memory\auto_update_watcher*") {
            $Blocked = $true
        }
    }

    if (-not $Blocked) {
        $Plan += [ordered]@{
            path = $Relative
            type = if ($Target.PSIsContainer) { "directory" } else { "file" }
            size_bytes = if ($Target.PSIsContainer) { 0 } else { $Target.Length }
            last_write = $Target.LastWriteTime.ToString("s")
            action = "delete_safe_cache_or_local_artifact"
        }
    }
}

$Report = [ordered]@{
    ok = $true
    name = "K-Uni Hygiene Engine"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    apply = [bool]$Apply
    protected_memory = @(
        "memoria evolutiva",
        "manifestos",
        "rollback",
        "cowork",
        "runtime",
        "codigo fonte",
        "Git"
    )
    planned_items = $Plan.Count
    planned_size_mb = [math]::Round((($Plan | ForEach-Object { $_.size_bytes } | Measure-Object -Sum).Sum / 1MB), 2)
    items = $Plan
}

if ($Apply) {
    foreach ($Item in $Plan) {
        $Path = $Item.path -replace "^\.\\", ""
        if (Test-Path $Path) {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    $Report.status = "cleanup_applied"
} else {
    $Report.status = "dry_run_only"
}

$Report | ConvertTo-Json -Depth 20 | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "K-UNI HYGIENE ENGINE"
Write-Host "Status:" $Report.status
Write-Host "Itens planejados:" $Report.planned_items
Write-Host "MB planejado:" $Report.planned_size_mb
Write-Host "Relatorio:" $ReportPath

if (-not $Apply) {
    Write-Host ""
    Write-Host "Dry-run apenas. Para limpar de verdade:"
    Write-Host 'powershell -ExecutionPolicy Bypass -File ".\ops\k_hygiene.ps1" -Apply'
}
