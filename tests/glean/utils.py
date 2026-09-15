import json
from pathlib import Path

import pytest

from manifests.testkey import sysname


def load_cases(caller_file: str) -> dict:
    """Load cases.json from the same directory as the calling test file."""
    return json.loads(
        (Path(caller_file).parent / "cases.json").read_text(encoding="utf-8")
    )


def skip_if_unstable(case: dict) -> None:
    """Skip a case carrying an `unstable` reason string in cases.json.

    `key.yaml` can only mark a whole test file, so per-case stability lives in the
    dataset. Called from the `case` fixture, so this runs before `driver` writes
    `json_metadata["test_case"]`. Without it the case is not reported to TestRail at
    all, the same as a test skipped through the manifest.

    The reason is a string to skip everywhere, or a dict keyed by platform the way
    `key.yaml` does it: {"win": "reason"}.
    """
    reason = case.get("unstable")
    if isinstance(reason, dict):
        reason = reason.get(sysname())
    if reason:
        pytest.skip(f"Unstable case: {reason}")
