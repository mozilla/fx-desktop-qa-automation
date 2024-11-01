from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "330168"


@pytest.fixture()
def add_prefs():
    return [("media.autoplay.default", 1), ("media.autoplay.enabled.user-gestures-needed", True)]


TEST_URL = "https://www.mlb.com/video/rockies-black-agree-on-extension"


def test_users_actions_saved_after_restart(driver: Firefox):
    """
    C330168: Verify that the users actions are saved after restart
    """
    # Instantiate objects
    nav = Navigation(driver)

    # Open Test page
    GenericPage(driver, url=TEST_URL).open()

    # Open the Site information panel and check "Allow Audio and Video"
    nav.click_on("autoplay-permission")
    nav.click_on("permission-popup-menulist-block-audio")
    nav.click_on("allow-audio-video-menuitem")
    nav.click_on("permission-popup-text")
    nav.click_on("autoplay-permission")

    # Refresh test page and check the site information panel shows "Allow Audio and Video"
    driver.get(driver.current_url)
    nav.click_on("autoplay-permission")
    with (driver.context(driver.CONTEXT_CHROME)):
        assert nav.get_element("permission-popup-menulist").is_displayed()
