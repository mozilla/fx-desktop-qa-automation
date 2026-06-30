import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation

SOURCE_URL = "https://example.com/?fbclid=1234"
EXPECTED_URL = "https://example.com/"


@pytest.fixture()
def test_case():
    return "2307354"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("privacy.query_stripping.strip_on_share.enabled", True),
        ("privacy.query_stripping.enabled", False),
    ]


def test_copy_clean_link(driver: Firefox):
    # Load source URL into address bar
    nav = Navigation(driver)
    nav.type_in_awesome_bar(SOURCE_URL)

    # Select URL and copy clean link from address bar
    nav.perform_key_combo_chrome(Keys.CONTROL, "l")
    nav.context_click_in_awesome_bar()
    nav.context_menu.click_and_hide_menu("context-menu-copy-clean-link")

    # Paste in a new tab and verify query params are stripped
    nav.open_and_switch_to_new_window("tab")
    nav.context_click_in_awesome_bar()
    nav.context_menu.click_and_hide_menu("context-menu-paste")

    # Paste fills the address bar asynchronously; poll the value until it
    # settles rather than reading it once, so a render/clipboard delay isn't
    # misread as a stripping failure.
    nav.element_attribute_is("awesome-bar", "value", EXPECTED_URL)
