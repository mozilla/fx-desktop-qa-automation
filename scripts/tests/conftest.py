"""Unit tests for scripts/ helpers.

The root conftest.py declares `driver` as autouse=True, so every collected test
would otherwise launch Firefox. These are pure unit tests, so the fixture is
overridden here with a no-op; pytest resolves `driver` to the closest
definition, which is this one.
"""

import pytest


@pytest.fixture(autouse=True)
def driver():
    yield None
