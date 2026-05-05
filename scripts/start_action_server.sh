#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p logs
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
echo "Starting Rasa action server on http://0.0.0.0:5055"
"./.venv/bin/python" -m rasa run actions --port 5055 2>&1 | tee -a logs/action-server.log
