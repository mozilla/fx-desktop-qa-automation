import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "3015392"


TEST_URL = "https://videojs.org/"


def test_html5_video_playback_controls(driver: Firefox):
    """
    C3015392 - Verify that HTML5 video playback and controls function as expected
    """

    # Instantiate object
    page = GenericPage(driver, url=TEST_URL)
    tabs = TabBar(driver)

    # Open test url
    page.open()

    # Use all available controls on the video player
    # Check play/pause buttons
    page.click_on("vjs-play-button")
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
    page.click_on("vjs-pause-button")
    page.element_visible("vjs-play")

    # Check full screen
    page.click_on("vjs-fullscreen")
    page.element_visible("vjs-exit-fullscreen")

    # Check exit full screen
    page.click_on("vjs-exit-fullscreen")
    page.element_visible("vjs-fullscreen")

    # Check volume
    page.click_on("vjs-volume")
    page.verify_volume_level(50)
