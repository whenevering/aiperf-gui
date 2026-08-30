#!/usr/bin/env bash
set -euo pipefail

: "${REGISTRY:=registry.intra.local}"
: "${NAMESPACE:=ai}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "${root}/config/env" ]; then
  # shellcheck disable=SC1091
  source "${root}/config/env"
fi

if [ -n "${REGISTRY_USER:-}" ] && [ -n "${REGISTRY_PASSWORD:-}" ]; then
  printf '%s' "$REGISTRY_PASSWORD" | docker login "$REGISTRY" -u "$REGISTRY_USER" --password-stdin
fi

docker tag nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0 "${REGISTRY}/${NAMESPACE}/aiperf:0.12.0"
docker tag aiperf-gui:0.1.0 "${REGISTRY}/${NAMESPACE}/aiperf-gui:0.12.0-2026-08-30"
docker tag aiperf-gui:0.1.0 "${REGISTRY}/${NAMESPACE}/aiperf-gui:latest"

docker push "${REGISTRY}/${NAMESPACE}/aiperf:0.12.0"
docker push "${REGISTRY}/${NAMESPACE}/aiperf-gui:0.12.0-2026-08-30"
docker push "${REGISTRY}/${NAMESPACE}/aiperf-gui:latest"
