import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330168"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("media.autoplay.default", 1),
        ("media.autoplay.enabled.user-gestures-needed", True),
    ]


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


def test_users_actions_saved_on_reload(driver: Firefox):
    """
    C330168: Verify that the users actions are saved after restart
    """
    # Instantiate objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    page = GenericPage(driver, url=TEST_URL)

    # Open Test page
    page.open()

    # Open the Audio-Video Permission panel and check "Allow Audio and Video"
    nav.open_audio_video_permission()

    # Refresh test page and check the site information panel shows "Allow Audio and Video"
    driver.get(driver.current_url)
    nav.element_visible("permission-popup-audio-video-allowed")

    # Check the Crossed off Play icon is no longer displayed
    nav.element_not_visible("autoplay-icon-blocked")

    # Check the website is added to the exceptions list in about:preferences#privacy
    about_prefs.open_autopaly_modal()
    about_prefs.element_visible("mlb-allow-audio-video-settings")

    # # Open Test page
    page.open()

    # Open the Site information panel and check "Block Audio and Video"
    nav.click_on("autoplay-icon-blocked")
    nav.click_on("permission-popup-audio-video-allowed")
    nav.click_and_hide_menu("block-audio-video-menuitem")

    # Refresh test page and check the site information panel shows "Block Audio and Video"
    driver.get(driver.current_url)
    nav.element_visible("permission-popup-audio-video-blocked")
    nav.element_visible("autoplay-icon-blocked")

    # Revisit test page and check Site information panel shows "Block Audio and Video"
    page.open()
    nav.element_visible("permission-popup-audio-video-blocked")

    # Check the Crossed off Play icon is displayed
    nav.element_visible("autoplay-icon-blocked")
