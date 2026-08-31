#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 aiperf-gui-0.12.0-YYYY-MM-DD.tar" >&2
  exit 2
fi

docker load -i "$1"
./run.sh
