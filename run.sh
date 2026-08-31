#!/usr/bin/env bash
set -euo pipefail

timezone_args=(-v /etc/localtime:/etc/localtime:ro)
if [ -f /etc/timezone ]; then
  timezone_args+=(-v /etc/timezone:/etc/timezone:ro)
fi
timezone="${TZ:-}"
if [ -z "$timezone" ] && [ -f /etc/timezone ]; then
  timezone="$(cat /etc/timezone)"
fi
if [ -z "$timezone" ]; then
  timezone="$(readlink -f /etc/localtime | sed 's#^/usr/share/zoneinfo/##')"
fi

docker rm -f aiperf-gui >/dev/null 2>&1 || true
docker run -d \
  --name aiperf-gui \
  -p 8080:8080 \
  -v aiperf-results:/data/results \
  -e TZ="$timezone" \
  "${timezone_args[@]}" \
  aiperf-gui:0.1.0
