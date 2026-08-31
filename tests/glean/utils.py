import json
from pathlib import Path

import pytest


def load_cases(caller_file: str) -> dict:
    """Load cases.json from the same directory as the calling test file."""
    return json.loads(
        (Path(caller_file).parent / "cases.json").read_text(encoding="utf-8")
    )


def skip_if_unstable(case: dict) -> None:
    """Skip a case carrying an `unstable` reason string in cases.json.

    `key.yaml` can only mark a whole test file, so per-case stability lives in the
    dataset. Called from the `case` fixture, so this runs before `driver` and reports
    as Untested, not Blocked.
    """
    reason = case.get("unstable")
    if reason:
        pytest.skip(f"Unstable case: {reason}")
