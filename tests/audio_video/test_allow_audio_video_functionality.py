import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330155"


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")
TEST_URL = "https://www.w3schools.com/html/mov_bbb.mp4"


@pytest.mark.skipif(
    WIN_GHA, reason="Audio playback not supported in Windows CI environment"
)
@pytest.mark.audio
@pytest.mark.noxvfb
def test_allow_audio_video_functionality(driver: Firefox):
    """
    C330155: 'Allow Audio and Video' functionality
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tabs = TabBar(driver)
    page = GenericPage(driver, url=TEST_URL)

    # Open privacy and security preferences and set 'Allow Audio and Video' for autoplay
    about_prefs.set_autoplay_setting_in_preferences("allow-audio-video")

    # Open the website in a new tab and check if the video starts playing with sound
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    page.open()
    tabs.expect_tab_sound_status(2, tabs.MEDIA_STATUS.PLAYING)
