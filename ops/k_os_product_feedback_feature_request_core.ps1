param(
    [ValidateSet("Init", "CreateDemo", "CreateFeedback", "CreateFeature", "LinkFeedback", "SetFeatureStatus", "SetFeaturePriority", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$CustomerAlias = "",

    [string]$FeedbackType = "feature_request",

    [string]$Category = "cockpit",

    [string]$Summary = "",

    [string]$Impact = "medium",

    [string]$Urgency = "medium",

    [string]$Sentiment = "neutral",

    [string]$Title = "",

    [string]$Effort = "medium",

    [string]$RevenueSignal = "none",

    [string]$Owner = "k_os_operator",

    [string]$NextAction = "",

    [string]$FeedbackId = "",

    [string]$FeatureId = "",

    [string]$Status = "",

    [string]$Priority = "",

    [string]$Reason = ""
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
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode create-demo
    }
    "CreateFeedback" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode create-feedback --customer-alias $CustomerAlias --feedback-type $FeedbackType --category $Category --summary $Summary --impact $Impact --urgency $Urgency --sentiment $Sentiment --owner $Owner
    }
    "CreateFeature" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode create-feature --title $Title --category $Category --impact $Impact --urgency $Urgency --effort $Effort --revenue-signal $RevenueSignal --owner $Owner --next-action $NextAction
    }
    "LinkFeedback" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode link-feedback --feedback-id $FeedbackId --feature-id $FeatureId --reason $Reason
    }
    "SetFeatureStatus" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode set-feature-status --feature-id $FeatureId --status $Status --reason $Reason
    }
    "SetFeaturePriority" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode set-feature-priority --feature-id $FeatureId --priority $Priority --reason $Reason
    }
    "Audit" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_product_feedback_feature_request_core.py" --mode show
    }
}