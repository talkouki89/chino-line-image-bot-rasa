$ErrorActionPreference = "Continue"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "Starting Rasa server on http://localhost:5005"
& cmd.exe /c '".\.venv\Scripts\python.exe" -m rasa run --enable-api --credentials credentials.yml --endpoints endpoints.yml --port 5005 2>&1' |
    Tee-Object -FilePath "logs\rasa-server.log" -Append
