import pytest


@pytest.fixture()
def suite_id():
    return ("2103", "Tabbed Browser")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [("browser.tabs.delayHidingAudioPlayingIconMS", "200")]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def video_url():
    return "https://www.youtube.com/watch?v=mAia0v3ojzw"
