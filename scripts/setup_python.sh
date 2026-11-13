#!/usr/bin/env bash
set -euo pipefail

pip3 install 'uv==0.11.18'
uv sync
