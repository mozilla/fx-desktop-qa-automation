import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330155"



TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


@pytest.fixture()
def firefox_options() -> Options:
    """
    Muting the browser prevents audio playback issues on Windows GHA runners
    while still allowing the video to play.
    """
    options = Options()
    options.set_preference("media.volume_scale", "0.0")
    return options


@pytest.mark.audio
@pytest.mark.noxvfb
def test_allow_audio_video_functionality(driver: Firefox):
    """
    C330155: 'Allow Audio and Video' functionality.
    """
    about_prefs = AboutPrefs(driver, category="permissionsData")
    tabs = TabBar(driver)
    page = GenericPage(driver, url=TEST_URL)

    # Allow websites to autoplay audio and video.
    about_prefs.set_autoplay_setting_in_preferences("allow-audio-video")

    # Open the test website and verify that the video starts playing.
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    page.open()

    tabs.expect_tab_sound_status(2, tabs.MEDIA_STATUS.PLAYING)
