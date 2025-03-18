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

@pytest.mark.headed
@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    """C134719, test that tabs can be muted and unmuted"""
    tabs = TabBar(driver)
    driver.get(video_url)

    # Dismiss cookie banner if present
    try:
        consent_button = driver.find_element(By.CSS_SELECTOR, COOKIE_CONSENT_SELECTOR)
        consent_button.click()
    except NoSuchElementException:
        pass  # Banner not displayed; proceed normally
    except ElementNotInteractableException:
        driver.execute_script("arguments[0].click();", consent_button)

    # Scroll the play button into view before clicking
    play_button = driver.find_element(By.CSS_SELECTOR, PLAY_BUTTON_SELECTOR)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", play_button)

    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
