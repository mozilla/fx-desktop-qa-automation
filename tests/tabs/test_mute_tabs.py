from os import environ

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from modules.browser_object import TabBar

@pytest.fixture()
def test_case():
    return "134719"

GHA = environ.get("GITHUB_ACTIONS") == "true"

@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    """C134719, test that tabs can be muted and unmuted"""
    tabs = TabBar(driver)
    driver.get(video_url)

    # Dismiss cookie banner if present
    try:
        consent_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label^='Accept all'], button[aria-label^='Accept the use']")
        consent_button.click()
    except NoSuchElementException:
        pass  # Banner was not displayed; proceed normally

    play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
    play_button.click()

    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
