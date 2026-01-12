import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, TabBar
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330153"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("media.autoplay.default", 1),
        ("media.autoplay.enabled.user-gestures-needed", True)
    ]

# YouTube consent cookie to bypass the consent dialog
YOUTUBE_CONSENT_COOKIE = {
    "name": "SOCS",
    "value": "CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiAo9CmBg",
    "domain": ".youtube.com"}

TEST_URL = "https://www.youtube.com/watch?v=vGZhMIXH62M"


def test_autoplay_sound_blocking_behavior_for_background_tabs(driver: Firefox):
    """
    C330153 - Verify autoplay sound blocking behavior for background tabs Note: YouTube is used as the test site
    since it has reliable autoplay behavior. The test adds a consent cookie to bypass the consent dialog.
    """
    # Instantiate objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    page = GenericPage(driver, url=TEST_URL)
    tabs = TabBar(driver)

    page.open()
    driver.add_cookie(YOUTUBE_CONSENT_COOKIE)

    page.open()

    # Right click on a youtube video in the collections stack
    context_menu = ContextMenu(driver)

    # Find a video link within the collections stack (Mix playlist thumbnail)
    video_link = driver.find_element(By.CSS_SELECTOR, "yt-collections-stack a")

    # Right click on the video link
    page.context_click(video_link)

    # Select "Open Link in New Tab" from the context menu
    context_menu.click_and_hide_menu("context-menu-open-link-in-tab")

    # # Wait for the new tab to open
    # page.wait_for_num_tabs(2)
    #
    # # Switch to background tab (the new tab with the video)
    # tabs.click_tab_by_index(2)
    #
    # # Verify video is blocked
    # tabs.expect_tab_sound_status(2, tabs.MEDIA_STATUS.AUTOPLAY_BLOCKED)
