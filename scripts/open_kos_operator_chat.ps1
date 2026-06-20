param()

$ErrorActionPreference="Continue";
$Root="C:\Users\oi\Desktop\motor-digital";
Set-Location $Root;

Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match "streamlit" -and $_.CommandLine -match "pages\\KOS_" } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue;
  };

Start-Sleep -Seconds 1;

Start-Process powershell -WindowStyle Minimized -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; python -m streamlit run pages\KOS_Operator_Chat.py --server.port 8523 --server.headless true`"";

Start-Sleep -Seconds 4;
Start-Process "http://localhost:8523";
