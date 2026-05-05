#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
"./.venv/bin/python" "./scripts/cleanup_runtime.py" "$@"
