import logging
from time import sleep

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar

PLAY_BUTTON_SELECTOR = ".ytp-play-button"
COOKIE_CONSENT_SELECTOR = (
    "button[aria-label^='Accept all'], button[aria-label^='Accept the use']"
)
RETRY_LIMIT = 10


@pytest.fixture()
def test_case():
    return "134719"


@pytest.fixture()
def add_to_prefs_list():
    return [("network.cookie.cookieBehavior", "2")]


@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    """C134719, test that tabs can be muted and unmuted"""
    tabs = TabBar(driver)
    driver.get(video_url)
    tabs.expect(EC.title_contains("mov_bbb.mp4"))

    with driver.context(driver.CONTEXT_CHROME):
        tab = tabs.get_tab(1)
        tabs.wait.until(
            lambda _: tab.get_attribute(tabs.MEDIA_STATUS.PLAYING) is not None
        )

        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
