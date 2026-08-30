#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 aiperf-0.12.0-gui1.tar" >&2
  exit 2
fi

docker load -i "$1"
./run.sh
