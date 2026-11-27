import pytest


@pytest.fixture(autouse=True)
def driver():
    """These tests don't start Firefox, so the suites' autouse driver is replaced."""
    return None
