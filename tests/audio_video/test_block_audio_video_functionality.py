import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330156"


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


def test_block_audio_video_functionality(driver: Firefox):
    """
    C330156: 'Block Audio and Video' functionality
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    nav = Navigation(driver)
    page = GenericPage(driver, url=TEST_URL)

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.set_autoplay_setting("block-audio-video")

    # Open test website and check the site is loaded and the featured video is not playing
    page.open()
    nav.click_on("autoplay-icon-blocked")
    nav.element_visible("permission-popup-audio-video-blocked")
