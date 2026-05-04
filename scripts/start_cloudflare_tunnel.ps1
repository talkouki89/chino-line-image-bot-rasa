$ErrorActionPreference = "Continue"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "Starting Cloudflare named tunnel: chino-line-image-bot-rasa"
& cmd.exe /c '".\tools\cloudflared.exe" tunnel run chino-line-image-bot-rasa 2>&1' |
    Tee-Object -FilePath "logs\cloudflared.log" -Append
