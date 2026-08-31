#!/usr/bin/env bash
set -euo pipefail

output="${1:-aiperf-gui-0.12.0-$(date +%F).tar}"

docker save aiperf-gui:0.1.0 -o "$output"
echo "Wrote $output"
