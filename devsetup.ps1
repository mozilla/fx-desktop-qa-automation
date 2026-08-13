Copy-Item .\scripts\pre-commit .\.git\hooks\ -Force

uv sync
if ($LASTEXITCODE -ne 0) {
    throw "uv sync failed with exit code $LASTEXITCODE"
}

uv run python .\scripts\switch_config.py dev
if ($LASTEXITCODE -ne 0) {
    throw "switch_config.py failed with exit code $LASTEXITCODE"
}