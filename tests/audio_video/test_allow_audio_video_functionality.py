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


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


# @pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
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

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.set_autoplay_setting("allow-audio-video")

    # Open the website and check if the video starts playing with sound
    page.open()
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
