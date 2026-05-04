$ErrorActionPreference = "Continue"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "Starting Rasa action server on http://localhost:5055"
& cmd.exe /c '".\.venv\Scripts\python.exe" -m rasa run actions --port 5055 2>&1' |
    Tee-Object -FilePath "logs\action-server.log" -Append
