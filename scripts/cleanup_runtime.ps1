$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root
& ".\.venv\Scripts\python.exe" ".\scripts\cleanup_runtime.py" @args
