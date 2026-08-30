#!/usr/bin/env bash
set -euo pipefail

docker save aiperf-gui:0.1.0 -o aiperf-0.12.0-gui1.tar
echo "Wrote aiperf-0.12.0-gui1.tar"
