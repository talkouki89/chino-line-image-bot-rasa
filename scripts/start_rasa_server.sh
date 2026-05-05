#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p logs
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
echo "Starting Rasa server on http://0.0.0.0:5005"
"./.venv/bin/python" -m rasa run --enable-api --credentials credentials.yml --endpoints endpoints.yml --port "${PORT:-5005}" 2>&1 | tee -a logs/rasa-server.log
