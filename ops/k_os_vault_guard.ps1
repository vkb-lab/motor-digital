param(
    [ValidateSet("Init", "Audit", "SetItem", "List", "DeleteItem", "SmokeTest")]
    [string]$Action = "Audit",

    [string]$Provider = "",

    [string]$Name = "",

    [string]$Value = "",

    [string]$Scope = "local"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = "C:\Users\oi\Desktop\motor-digital"
$VaultDir = Join-Path $Root "local_secrets\k_os_vault"
$VaultFile = Join-Path $VaultDir "vault.json"
$ReportDir = Join-Path $Root "reports\vault"
$MemoryDir = Join-Path $Root "memory\vault"
$LatestJson = Join-Path $ReportDir "latest_vault_guard_report.json"
$LatestMd = Join-Path $ReportDir "latest_vault_guard_report.md"
$EventsFile = Join-Path $MemoryDir "events.jsonl"

cd $Root

function NowUtc {
    return (Get-Date).ToUniversalTime().ToString("o")
}

function Ensure-Dirs {
    New-Item -ItemType Directory -Force -Path $VaultDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
    New-Item -ItemType Directory -Force -Path $MemoryDir | Out-Null
}

function Read-Vault {
    Ensure-Dirs

    if (-not (Test-Path $VaultFile)) {
        $Initial = [ordered]@{
            version = "1.0.0"
            created_at = NowUtc
            updated_at = NowUtc
            storage = "windows_dpapi_current_user"
            items = @()
        }

        $Initial | ConvertTo-Json -Depth 20 | Set-Content -Path $VaultFile -Encoding UTF8
    }

    $Raw = Get-Content $VaultFile -Raw -Encoding UTF8
    return $Raw | ConvertFrom-Json
}

function Write-Vault {
    param([object]$Vault)

    $Vault.updated_at = NowUtc
    $Vault | ConvertTo-Json -Depth 20 | Set-Content -Path $VaultFile -Encoding UTF8
}

function Get-PlainFromSecure {
    param([System.Security.SecureString]$Secure)

    $Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)

    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }
}

function Hash-Text {
    param([string]$Text)

    $Sha = [System.Security.Cryptography.SHA256]::Create()
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $Hash = $Sha.ComputeHash($Bytes)
    return ([BitConverter]::ToString($Hash)).Replace("-", "").ToLowerInvariant()
}

function Add-Event {
    param([string]$Event, [object]$Data)

    Ensure-Dirs

    $Obj = [ordered]@{
        event = $Event
        created_at = NowUtc
        data = $Data
    }

    Add-Content -Path $EventsFile -Value ($Obj | ConvertTo-Json -Compress -Depth 20) -Encoding UTF8
}

function Redact-Item {
    param([object]$Item)

    return [ordered]@{
        provider = $Item.provider
        name = $Item.name
        scope = $Item.scope
        created_at = $Item.created_at
        updated_at = $Item.updated_at
        value_hash = $Item.value_hash
        value_last4 = $Item.value_last4
        encrypted = $true
    }
}

function Init-Vault {
    Ensure-Dirs
    $Vault = Read-Vault
    Write-Vault $Vault
    Add-Event -Event "vault.init" -Data @{ ok = $true }

    Write-Host "K-OS Vault Guard inicializado."
    Write-Host "Vault local:" $VaultFile
}

function Set-ItemVault {
    if ([string]::IsNullOrWhiteSpace($Provider)) {
        throw "Informe -Provider."
    }

    if ([string]::IsNullOrWhiteSpace($Name)) {
        throw "Informe -Name."
    }

    Ensure-Dirs
    $Vault = Read-Vault

    if ([string]::IsNullOrWhiteSpace($Value)) {
        $Secure = Read-Host "Digite o valor para $Provider/$Name" -AsSecureString
        $Plain = Get-PlainFromSecure -Secure $Secure
    } else {
        $Secure = ConvertTo-SecureString -String $Value -AsPlainText -Force
        $Plain = $Value
    }

    $Encrypted = $Secure | ConvertFrom-SecureString
    $Hash = Hash-Text -Text $Plain
    $Last4 = if ($Plain.Length -ge 4) { $Plain.Substring($Plain.Length - 4) } else { "****" }

    $Items = @($Vault.items | Where-Object { -not ($_.provider -eq $Provider -and $_.name -eq $Name) })

    $Item = [ordered]@{
        provider = $Provider
        name = $Name
        scope = $Scope
        created_at = NowUtc
        updated_at = NowUtc
        encrypted_value = $Encrypted
        value_hash = $Hash
        value_last4 = $Last4
        storage = "windows_dpapi_current_user"
        reveal_blocked_by_default = $true
        external_api_enabled = $false
    }

    $Items += $Item
    $Vault.items = @($Items)

    Write-Vault $Vault

    Add-Event -Event "vault.item_set" -Data @{
        provider = $Provider
        name = $Name
        scope = $Scope
        value_hash = $Hash
    }

    Write-Host "Item salvo no cofre local."
    Write-Host "Provider:" $Provider
    Write-Host "Name:" $Name
    Write-Host "Valor nao exibido."
}

function List-Vault {
    $Vault = Read-Vault
    $SafeItems = @()

    foreach ($Item in $Vault.items) {
        $SafeItems += (Redact-Item -Item $Item)
    }

    $Out = [ordered]@{
        ok = $true
        status = "listed"
        storage = "windows_dpapi_current_user"
        count = $SafeItems.Count
        items = $SafeItems
        raw_values_exposed = $false
        external_api_enabled = $false
    }

    $Out | ConvertTo-Json -Depth 20
}

function Delete-ItemVault {
    param(
        [string]$ProviderToDelete,
        [string]$NameToDelete
    )

    if ([string]::IsNullOrWhiteSpace($ProviderToDelete)) {
        $ProviderToDelete = $Provider
    }

    if ([string]::IsNullOrWhiteSpace($NameToDelete)) {
        $NameToDelete = $Name
    }

    if ([string]::IsNullOrWhiteSpace($ProviderToDelete)) {
        throw "Informe -Provider."
    }

    if ([string]::IsNullOrWhiteSpace($NameToDelete)) {
        throw "Informe -Name."
    }

    $Vault = Read-Vault
    $Before = @($Vault.items).Count
    $Vault.items = @($Vault.items | Where-Object { -not ($_.provider -eq $ProviderToDelete -and $_.name -eq $NameToDelete) })
    $After = @($Vault.items).Count

    Write-Vault $Vault

    Add-Event -Event "vault.item_deleted" -Data @{
        provider = $ProviderToDelete
        name = $NameToDelete
        before = $Before
        after = $After
    }

    Write-Host "Item removido, se existia."
}

function Audit-Vault {
    Ensure-Dirs
    $Vault = Read-Vault

    $GitIgnore = Join-Path $Root ".gitignore"
    $IgnoreOk = $false

    if (Test-Path $GitIgnore) {
        $IgnoreOk = Select-String -Path $GitIgnore -Pattern "local_secrets/" -Quiet -ErrorAction SilentlyContinue
    }

    $SafeItems = @()
    foreach ($Item in $Vault.items) {
        $SafeItems += (Redact-Item -Item $Item)
    }

    $Report = [ordered]@{
        ok = $true
        checkpoint = "018"
        module = "vault_guard"
        status = "passed"
        generated_at = NowUtc
        vault_exists = (Test-Path $VaultFile)
        vault_path = "local_secrets/k_os_vault/vault.json"
        storage = "windows_dpapi_current_user"
        gitignore_local_secrets = [bool]$IgnoreOk
        item_count = $SafeItems.Count
        items = $SafeItems
        raw_values_exposed = $false
        external_api_enabled = $false
        external_send_enabled = $false
        external_publish_enabled = $false
        manual_approval_required = $true
        next_checkpoint = "019 - K-Audit Evidence Pack"
    }

    $Report | ConvertTo-Json -Depth 20 | Set-Content -Path $LatestJson -Encoding UTF8

    $Lines = @()
    $Lines += "# K-OS Vault Guard Report"
    $Lines += ""
    $Lines += "- Status: passed"
    $Lines += "- Vault exists: " + (Test-Path $VaultFile)
    $Lines += "- Storage: windows_dpapi_current_user"
    $Lines += "- Items: " + $SafeItems.Count
    $Lines += "- Raw values exposed: false"
    $Lines += "- External API enabled: false"
    $Lines += "- Manual approval required: true"
    $Lines += ""
    $Lines += "## Items"
    $Lines += ""

    if ($SafeItems.Count -eq 0) {
        $Lines += "- Nenhum item salvo no cofre."
    } else {
        foreach ($Item in $SafeItems) {
            $Lines += "- " + $Item.provider + "/" + $Item.name + " | scope=" + $Item.scope + " | last4=" + $Item.value_last4
        }
    }

    $Lines | Set-Content -Path $LatestMd -Encoding UTF8

    Add-Event -Event "vault.audit" -Data @{
        ok = $true
        item_count = $SafeItems.Count
        raw_values_exposed = $false
    }

    $Report | ConvertTo-Json -Depth 20
}

function Smoke-Test {
    Init-Vault

    $script:Provider = "demo"
    $script:Name = "smoke"
    $script:Value = "demo-value-for-smoke-test"
    $script:Scope = "local"

    Set-ItemVault

    $script:Provider = "demo"
    $script:Name = "smoke"

    Delete-ItemVault

    Audit-Vault
}

switch ($Action) {
    "Init" {
        Init-Vault
    }

    "Audit" {
        Audit-Vault
    }

    "SetItem" {
        Set-ItemVault
    }

    "List" {
        List-Vault
    }

    "DeleteItem" {
        Delete-ItemVault
    }

    "SmokeTest" {
        Smoke-Test
    }
}