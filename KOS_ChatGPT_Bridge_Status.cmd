@echo off
cd /d C:\Users\oi\Desktop\motor-digital
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kos_chatgpt_bridge_runtime_control.ps1 -Action status
pause
