#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "${root}/config/env" ]; then
  # shellcheck disable=SC1091
  source "${root}/config/env"
fi

: "${GITEA_REPO_URL:?Set GITEA_REPO_URL, for example http://gitea.intra.local/ai/aiperf-gui.git}"

workdir="${root}/work"

mkdir -p "$workdir"
rm -rf "${workdir}/aiperf-gui"

git clone "${root}/source/aiperf-gui.git.bundle" "${workdir}/aiperf-gui"
cd "${workdir}/aiperf-gui"
git remote set-url origin "$GITEA_REPO_URL"
git push -u origin main
git push --tags || true

echo "Imported to $GITEA_REPO_URL"
