#!/usr/bin/env bash
set -euo pipefail

: "${REGISTRY:=registry.intra.local}"
: "${NAMESPACE:=ai}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "${root}/config/env" ]; then
  # shellcheck disable=SC1091
  source "${root}/config/env"
fi

image="${REGISTRY}/${NAMESPACE}/aiperf-gui:latest"

docker rm -f aiperf-gui >/dev/null 2>&1 || true
docker run -d \
  --name aiperf-gui \
  -p 8080:8080 \
  -v aiperf-results:/data/results \
  "$image"

sleep 3
docker ps --filter name=aiperf-gui
curl -fsS http://127.0.0.1:8080/health
echo
curl -fsS http://127.0.0.1:8080/api/aiperf-info
echo
