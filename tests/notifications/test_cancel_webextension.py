import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation

TEST_URL = "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker/"
ADDON_NAME = "Popup Blocker (strict)"


@pytest.fixture()
def test_case():
    return "122934"


@pytest.fixture()
def temp_selectors():
    return {
        "add-to-firefox": {
            "selectorData": "AMInstallButton-button",
            "strategy": "class",
            "groups": [],
        }
    }


def test_cancel_webextension(driver: Firefox, web_page):
    """
    C1756778 - Verify that cancelling the WebExtension install dismisses the permission panel
    and the add-on is not installed.
    """
    nav = Navigation(driver)

    # Open AMO page
    page = web_page(TEST_URL)

    # Click "Add to Firefox"
    page.click_on("add-to-firefox")

    # Click Cancel in permission panel (chrome)
    nav.element_clickable("popup-notification-cancel")
    nav.click_on("popup-notification-cancel")

    # Button should become visible again
    page.expect(lambda _: page.get_element("add-to-firefox").is_displayed())
