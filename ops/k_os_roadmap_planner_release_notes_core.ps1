param(
    [ValidateSet("Init", "CreateDemo", "CreateRelease", "AddFeature", "SetReleaseStatus", "GenerateReleaseNotes", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Title = "",

    [string]$VersionLabel = "",

    [string]$ReleaseType = "minor",

    [string]$Channel = "internal",

    [string]$TargetDate = "",

    [string]$Owner = "k_os_operator",

    [string]$ReleaseId = "",

    [string]$FeatureId = "",

    [string]$Status = "",

    [string]$Reason = "",

    [string]$Audience = "internal"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

switch ($Action) {
    "Init" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode create-demo
    }
    "CreateRelease" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode create-release --title $Title --version-label $VersionLabel --release-type $ReleaseType --channel $Channel --target-date $TargetDate --owner $Owner
    }
    "AddFeature" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode add-feature --release-id $ReleaseId --feature-id $FeatureId --reason $Reason
    }
    "SetReleaseStatus" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode set-release-status --release-id $ReleaseId --status $Status --reason $Reason
    }
    "GenerateReleaseNotes" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode generate-release-notes --release-id $ReleaseId --audience $Audience
    }
    "Audit" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_roadmap_planner_release_notes_core.py" --mode show
    }
}