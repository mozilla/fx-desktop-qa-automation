import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi

TEST_URL = "example.com"


@pytest.fixture()
def test_case():
    return "1362263"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("dom.security.https_first_pbm", True)
    ]


def test_https_first_mode_enabled_in_private_browsing_without_protocol(driver: Firefox):
    """
    C1362263 - Check that HTTPS First Mode is properly enabled and working in Private Browsing - when protocol is not mentioned
    """

    # Instantiate objects
    panel = PanelUi(driver)
    nav = Navigation(driver)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Access example.com
    nav.search(TEST_URL)

    # Check that the connection is HTTPS
    panel.url_contains("https://")
