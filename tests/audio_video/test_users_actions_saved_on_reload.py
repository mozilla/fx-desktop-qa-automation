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

    # Open the test page
    page.open()

    # Open the Audio-Video Permission panel and check "Allow Audio and Video"
    nav.set_site_autoplay_permission("allow-audio-video")

    # Refresh test page and check the Audio-Video Permission panel shows "Allow Audio and Video" and the crossed off
    # Play icon is no longer displayed
    driver.get(driver.current_url)
    nav.verify_autoplay_state("allow")

    # Check the website is added to the exceptions list in about:preferences#privacy
    about_prefs.open_autoplay_modal()
    about_prefs.element_visible("mlb-allow-audio-video-settings")

    # # Open the test page
    page.open()

    # Open the Audio-Video Permission panel and check "Block Audio and Video"
    nav.set_site_autoplay_permission("block-audio-video")

    # Refresh test page and check the Audio-Video Permission panel shows "Block Audio and Video"
    driver.get(driver.current_url)
    nav.verify_autoplay_state("block")

    # Revisit test page and check Site information panel shows "Block Audio and Video"
    page.open()
    nav.verify_autoplay_state("block")
