import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "330156"


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


def test_allow_audio_video_functionality(driver: Firefox):
    """
    C330156: 'Block Audio and Video' functionality
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    nav = Navigation(driver)

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.open()
    about_prefs.get_element("autoplay-settings-button").click()

    # Get the web element for the iframe
    iframe = about_prefs.get_iframe()
    ba.switch_to_iframe_context(iframe)

    # Click on the autoplay settings for all websites
    about_prefs.get_element("autoplay-settings").click()

    # Choose block audio and video and save changes
    about_prefs.click_on("block-audio-video")
    about_prefs.get_element("spacer").click()
    about_prefs.get_element("autoplay-save-changes").click()

    # Open test website and check the site is loaded and the featured video is not playing
    GenericPage(driver, url=TEST_URL).open()
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("autoplay-permission").click()
        assert nav.get_element("permission-popup-menulist").is_displayed()
