#!/usr/bin/env bash
set -euo pipefail

readonly UV_VERSION="0.11.18"
readonly UV_USER_BIN="$(python3 -m site --user-base)/bin"

python3 -m pip install "uv==$UV_VERSION"

# Keep user-level pip installs available now and in later GitHub Actions steps.
export PATH="$UV_USER_BIN:$PATH"
if [[ -n "${GITHUB_PATH:-}" ]]; then
  printf '%s\n' "$UV_USER_BIN" >> "$GITHUB_PATH"
fi

uv --version
uv sync
