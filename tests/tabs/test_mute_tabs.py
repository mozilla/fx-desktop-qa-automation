import sys
from os import environ

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar

PLAY_BUTTON_SELECTOR = ".ytp-play-button"
COOKIE_CONSENT_SELECTOR = (
    "button[aria-label^='Accept all'], button[aria-label^='Accept the use']"
)
WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.fixture()
def test_case():
    return "134719"


@pytest.fixture()
def add_to_prefs_list():
    return [("network.cookie.cookieBehavior", "2")]


@pytest.mark.skipif(WIN_GHA, reason="Test unstable on Windows in Github Actions")
@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    """C134719, test that tabs can be muted and unmuted"""
    tabs = TabBar(driver)
    driver.get(video_url)
    tabs.expect(EC.title_contains("mov_bbb.mp4"))

    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
