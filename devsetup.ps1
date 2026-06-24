Copy-Item .\scripts\pre-commit .\.git\hooks\ -Force
uv sync
uv scripts\switch_config.py dev
