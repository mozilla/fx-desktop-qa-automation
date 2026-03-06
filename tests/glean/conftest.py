import pytest


@pytest.fixture()
def suite_id():
    return ("TODO", "Glean SERP Telemetry")


@pytest.fixture()
def prefs_list(add_to_prefs_list):
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
