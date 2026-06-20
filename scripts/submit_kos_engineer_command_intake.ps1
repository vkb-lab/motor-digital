param(
  [switch]$FromClipboard,
  [string]$Text = "",
  [string]$File = ""
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

New-Item -ItemType Directory -Force "local_runtime\kos_engineer_command_intake\incoming" | Out-Null;

$InputText = "";

if($FromClipboard){
  $InputText = Get-Clipboard -Raw;
} elseif(-not [string]::IsNullOrWhiteSpace($File)) {
  $InputText = Get-Content $File -Raw -Encoding UTF8;
} elseif(-not [string]::IsNullOrWhiteSpace($Text)) {
  $InputText = $Text;
} else {
  throw "Informe -FromClipboard, -File ou -Text."
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss";
$InboxFile = "local_runtime\kos_engineer_command_intake\incoming\engineer_packet_$Stamp.txt";

$InputText | Set-Content $InboxFile -Encoding UTF8;

python scripts\run_phase69i_engineer_command_intake.py --text-file $InboxFile;
