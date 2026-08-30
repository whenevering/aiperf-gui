#!/usr/bin/env bash
set -euo pipefail

docker rm -f aiperf-gui >/dev/null 2>&1 || true
docker run -d \
  --name aiperf-gui \
  -p 8080:8080 \
  -v aiperf-results:/data/results \
  aiperf-gui:0.1.0
