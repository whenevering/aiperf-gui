#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

(cd "${root}/images" && sha256sum -c aiperf-base-0.12.0.sha256)
(cd "${root}/images" && sha256sum -c aiperf-gui-0.12.0-2026-08-30.sha256)

docker load -i "${root}/images/aiperf-base-0.12.0.tar"
docker load -i "${root}/images/aiperf-gui-0.12.0-2026-08-30.tar"

docker images | grep -E 'aiperf|ai-dynamo' || true
