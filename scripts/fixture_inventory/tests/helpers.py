import textwrap
from pathlib import Path


def write_files(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    return root


def by_id(inv: dict) -> dict[str, dict]:
    return {f["id"]: f for f in inv["fixtures"]}
