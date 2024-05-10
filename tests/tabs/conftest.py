import pytest


@pytest.fixture()
def suite_id():
    return ("2103", "Tabbed Browsing")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []

@pytest.fixture()
def video_url():
    return "https://www.youtube.com/watch?v=mAia0v3ojzw"
