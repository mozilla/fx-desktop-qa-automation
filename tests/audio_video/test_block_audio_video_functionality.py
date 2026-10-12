import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object import AboutConfig
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "4108465"


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"
AUTOPLAY_PREF = "media.autoplay.default"
BLOCK_AUDIO_VIDEO_VALUE = "5"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.aboutConfig.showWarning", False),
    ]


def test_block_audio_video_functionality(driver: Firefox):
    """
    C4108465: 'Block Audio and Video' functionality
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="permissionsData")
    about_config = AboutConfig(driver)
    nav = Navigation(driver)
    page = GenericPage(driver, url=TEST_URL)

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.set_autoplay_setting_in_preferences("block-audio-video")

    # Open test website and check the site is loaded and the featured video is not playing
    page.open()
    nav.click_on("autoplay-icon-blocked")
    nav.verify_autoplay_state("block")

    # Verify media.autoplay.default in about:config reflects Block Audio and Video
    assert about_config.get_pref_value(AUTOPLAY_PREF) == BLOCK_AUDIO_VIDEO_VALUE
