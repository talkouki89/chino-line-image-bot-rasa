#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p logs
: "${CLOUDFLARE_TUNNEL_NAME:=chino-line-image-bot-rasa}"
echo "Starting Cloudflare Tunnel: ${CLOUDFLARE_TUNNEL_NAME}"
cloudflared tunnel run "${CLOUDFLARE_TUNNEL_NAME}" 2>&1 | tee -a logs/cloudflared.log
