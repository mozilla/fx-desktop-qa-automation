import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "143627"


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
def test_allow_audio_video_functionality(driver: Firefox):
    """
    C330155 : 'Allow Audio and Video' functionality
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    tabs = TabBar(driver)

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.open()
    about_prefs.get_element("autoplay-settings-button").click()

    # Get the web element for the iframe
    iframe = about_prefs.get_iframe()
    ba.switch_to_iframe_context(iframe)

    # Click on the autoplay settings for all websites
    about_prefs.get_element("autoplay-settings").click()

    # Choose allow audio and video and save changes
    about_prefs.click_on("allow-audio-video")
    about_prefs.get_element("spacer").click()
    about_prefs.get_element("autoplay-save-changes").click()

    # Open test website and check the site is loaded and the featured video starts playing with sound
    GenericPage(driver, url=TEST_URL).open()
    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
