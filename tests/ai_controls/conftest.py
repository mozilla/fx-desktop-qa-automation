import pytest


@pytest.fixture()
def suite_id():
    return ("SAI", "AI Controls")


@pytest.fixture()
def prefs_list():
    """Provide an empty prefs list for the driver fixture."""
    return []
