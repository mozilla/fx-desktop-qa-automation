import pytest


@pytest.fixture()
def suite_id():
    return ("S22801", "Language Packs")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.liveReload", True),
    ]
