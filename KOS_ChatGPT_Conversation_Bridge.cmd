@echo off
cd /d C:\Users\oi\Desktop\motor-digital
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_kos_chatgpt_conversation_bridge.ps1 -OpenConversation -OpenFolder
pause
