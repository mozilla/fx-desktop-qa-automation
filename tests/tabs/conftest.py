import pytest


@pytest.fixture()
def suite_id():
    return ("2103", "Tabbed Browser")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("browser.tabs.delayHidingAudioPlayingIconMS", "200")]


@pytest.fixture()
def video_url():
    return "https://www.youtube.com/watch?v=mAia0v3ojzw"
