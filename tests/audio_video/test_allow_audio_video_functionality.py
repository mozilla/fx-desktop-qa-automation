import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330155"


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


@pytest.fixture()
def add_to_prefs_list():
    """
    Muting the browser prevents audio playback issues on Windows GHA runners
    while still allowing the video to play.
    """
    return [("media.volume_scale", "0.0")]


def video_is_playing(driver: Firefox) -> bool:
    """
    Return True when an unmuted video has started playback.
    """
    try:
        videos = driver.find_elements(By.TAG_NAME, "video")

        for video in videos:
            state = driver.execute_script(
                """
                const video = arguments[0];

                return {
                    paused: video.paused,
                    muted: video.muted,
                    volume: video.volume,
                    currentTime: video.currentTime,
                    readyState: video.readyState
                };
                """,
                video,
            )

            if (
                not state["paused"]
                and not state["muted"]
                and state["volume"] > 0
                and state["currentTime"] > 0
                and state["readyState"] >= 2
            ):
                return True

    except StaleElementReferenceException:
        return False

    return False


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

    # Verify that an unmuted video starts playing.
    WebDriverWait(driver, 30).until(
        video_is_playing,
        message="The video did not begin unmuted playback within 30 seconds.",
    )
