import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "122933"


@pytest.fixture()
def temp_selectors():
    return {
        "add-to-firefox": {
            "selectorData": "AMInstallButton-button",
            "strategy": "class",
            "groups": [],
        }
    }


TEST_URL = "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker/"


def test_webextension_completed_installation_successfully_displayed(
    driver: Firefox, temp_selectors
):
    """
    C122933 - Verify that WebExtension completed installation is successfully displayed
    """
    # Instantiate object
    nav = Navigation(driver)
    test_page = GenericPage(driver, url=TEST_URL).open()
    test_page.elements |= temp_selectors

    # Click add to Firefox
    test_page.click_on("add-to-firefox")

    # Click the Add button
    nav.element_clickable("popup-notification-add")
    nav.click_on("popup-notification-add")

    # The WebExtension completed installation panel is successfully displayed
    nav.expect_element_attribute_contains("popup-notification-primary-button", "label", "OK")
    nav.expect_element_attribute_contains(
        "popup-notification-panel", "name", "Popup Blocker (strict)"
    )
    nav.expect_element_attribute_contains(
        "popup-notification-panel", "endlabel", " was added."
    )
