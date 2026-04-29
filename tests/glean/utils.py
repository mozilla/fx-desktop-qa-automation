import json
from pathlib import Path


def load_cases(caller_file: str) -> dict:
    """Load cases.json from the same directory as the calling test file."""
    return json.loads(
        (Path(caller_file).parent / "cases.json").read_text(encoding="utf-8")
    )
