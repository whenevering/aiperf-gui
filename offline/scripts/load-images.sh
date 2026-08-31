#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gui_image_archive="${AIPERF_GUI_ARCHIVE:-aiperf-gui-0.1.0-2026-08-31.tar.gz}"
gui_sha_file="${AIPERF_GUI_SHA_FILE:-${gui_image_archive}.sha256}"

(cd "${root}/images" && sha256sum -c aiperf-base-0.12.0.sha256)
(cd "${root}/images" && sha256sum -c "${gui_sha_file}")

docker load -i "${root}/images/aiperf-base-0.12.0.tar"
docker load -i "${root}/images/${gui_image_archive}"

docker images | grep -E 'aiperf|ai-dynamo' || true
