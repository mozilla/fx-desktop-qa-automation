from os import environ

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from modules.browser_object import TabBar

PLAY_BUTTON_SELECTOR = ".ytp-play-button"
COOKIE_CONSENT_SELECTOR = "button[aria-label^='Accept all'], button[aria-label^='Accept the use']"

@pytest.fixture()
def test_case():
    return "134719"

GHA = environ.get("GITHUB_ACTIONS") == "true"

@pytest.mark.skipif(GHA, reason="Test unstable in Github Actions")
@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    """C134719, test that tabs can be muted and unmuted"""
    tabs = TabBar(driver)
    driver.get(video_url)

    # Dismiss cookie banner if present
    try:
        consent_button = driver.find_element(By.CSS_SELECTOR, COOKIE_CONSENT_SELECTOR)
        consent_button.click()
    except (NoSuchElementException, ElementNotInteractableException):
        pass  # Banner wasn't displayed or not interactable; proceed normally

    play_button = driver.find_element(By.CSS_SELECTOR, PLAY_BUTTON_SELECTOR)
    play_button.click()

    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
