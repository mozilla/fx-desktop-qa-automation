import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_base import BasePage
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "330153"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("media.autoplay.default", 1),
        ("media.autoplay.enabled.user-gestures-needed", True),
    ]


# Injects YouTube SOCS consent cookie to bypass region/AB tested consent flows that can block interaction with the
# watch page DOM. This is a pragmatic shortcut for this test, but is not a general best practice, so it should be
# used only when absolutely necessary.
YOUTUBE_CONSENT_COOKIE = {
    "name": "SOCS",
    "value": "CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiAo9CmBg",
    "domain": ".youtube.com",
}

TEST_URL = "https://www.youtube.com/watch?v=vGZhMIXH62M"

# Temporary selector for a recommended video link on YouTube watch pages
VIDEO_LINK_SELECTOR = (
    By.CSS_SELECTOR,
    "yt-lockup-view-model a.yt-lockup-view-model__content-image[href^='/watch']",
)


@BasePage.context_content
def _context_click_video_link(page: GenericPage) -> None:
    """
    In content context, locate a YouTube video link and right click it. Helper method, not in Pom/Bom
    structure, although it requires context switching, because it's very specific to this test.
    """
    page.expect(EC.element_to_be_clickable(VIDEO_LINK_SELECTOR))
    page.context_click(VIDEO_LINK_SELECTOR)


def test_autoplay_sound_blocking_behavior_for_background_tabs(driver: Firefox):
    """
    C330153 - Verify Firefox blocks audible autoplay in a background tab and reflects the expected UI indicators.
    Note:
        The test uses YouTube watch pages (with a consent handling workaround) because the nature of the test is
    restricted to realistic user behavior patterns that involve opening a link to another video in a background tab
    from an existing video watch page while having, a simple/static page  des not reproduce the same player
    initialization, navigation patterns, or background tab autoplay behavior.
    """
    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    tabs = TabBar(driver)
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    # Open watch page, set consent cookie, then reload so the DOM is available without interference
    page.open()
    driver.add_cookie(YOUTUBE_CONSENT_COOKIE)
    page.open()

    # Right-click a YouTube recommended video link
    _context_click_video_link(page)

    # Open the link in a background tab
    context_menu.click_and_hide_menu("context-menu-open-link-in-tab")
    tabs.wait_for_num_tabs(2)

    # Play Tab button is displayed on the background tab
    tabs.expect_play_tab_button(visible=True)

    # Switch to the new tab, URL bar shows autoplay blocked icon
    tabs.click_tab_by_index(2)

    nav.expect_autoplay_blocked_icon(visible=True)

    # Play Tab button is no longer displayed on the tab
    tabs.expect_play_tab_button(visible=False)
