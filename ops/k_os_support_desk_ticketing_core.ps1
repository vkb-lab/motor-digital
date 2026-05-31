param(
    [ValidateSet("Init", "CreateDemo", "CreateTicket", "SetStatus", "SetPriority", "AddNote", "Audit", "Show")]
    [string]$Action = "Audit",

    [string]$CustomerAlias = "",

    [string]$Category = "question",

    [string]$Priority = "medium",

    [string]$Subject = "",

    [string]$Summary = "",

    [string]$Owner = "k_os_operator",

    [string]$TicketId = "",

    [string]$Status = "",

    [string]$Reason = "",

    [string]$NoteType = "internal"
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
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode init
    }
    "CreateDemo" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode create-demo
    }
    "CreateTicket" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode create-ticket --customer-alias $CustomerAlias --category $Category --priority $Priority --subject $Subject --summary $Summary --owner $Owner
    }
    "SetStatus" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode set-status --ticket-id $TicketId --status $Status --reason $Reason
    }
    "SetPriority" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode set-priority --ticket-id $TicketId --priority $Priority --reason $Reason
    }
    "AddNote" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode add-note --ticket-id $TicketId --summary $Summary --note-type $NoteType --owner $Owner
    }
    "Audit" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode audit
    }
    "Show" {
        & $Python "ops\k_os_support_desk_ticketing_core.py" --mode show
    }
}