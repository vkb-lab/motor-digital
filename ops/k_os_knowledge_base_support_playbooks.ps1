param(
    [ValidateSet("Init", "CreateDemo", "CreateArticle", "CreatePlaybook", "AddTemplate", "LinkTicket", "SetArticleStatus", "SetPlaybookStatus", "GenerateDraft", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$Title = "",

    [string]$Category = "support",

    [string]$Summary = "",

    [string]$Content = "",

    [string]$Steps = "",

    [string]$Owner = "k_os_operator",

    [string]$TicketId = "",

    [string]$ArticleId = "",

    [string]$PlaybookId = "",

    [string]$TemplateId = "",

    [string]$Status = "",

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
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode create-demo
    }
    "CreateArticle" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode create-article --title $Title --category $Category --summary $Summary --content $Content --owner $Owner
    }
    "CreatePlaybook" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode create-playbook --title $Title --category $Category --steps $Steps --owner $Owner
    }
    "AddTemplate" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode add-template --title $Title --category $Category --content $Content --owner $Owner
    }
    "LinkTicket" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode link-ticket --ticket-id $TicketId --article-id $ArticleId --playbook-id $PlaybookId --reason $Reason
    }
    "SetArticleStatus" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode set-article-status --article-id $ArticleId --status $Status --reason $Reason
    }
    "SetPlaybookStatus" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode set-playbook-status --playbook-id $PlaybookId --status $Status --reason $Reason
    }
    "GenerateDraft" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode generate-draft --ticket-id $TicketId --template-id $TemplateId
    }
    "Audit" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_knowledge_base_support_playbooks.py" --mode show
    }
}