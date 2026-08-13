#!/bin/sh

cp -f ./scripts/pre-commit ./.git/hooks/pre-commit;
uv sync; uv run python3 scripts/switch_config.py dev
