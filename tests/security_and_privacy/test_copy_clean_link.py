import sys

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation

SOURCE_URL = "https://www.example.com/?fbclid=1234"
EXPECTED_URL = "https://www.example.com/"


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
    nav = Navigation(driver)
    modifier_key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL

    # Open the URL containing the tracking parameter.
    driver.get(SOURCE_URL)

    # Select the URL and copy the clean link.
    nav.perform_key_combo_chrome(modifier_key, "l")
    nav.context_click_in_awesome_bar()
    nav.context_menu.click_and_hide_menu("context-menu-copy-clean-link")

    # Open a new tab and paste the copied link once.
    nav.open_and_switch_to_new_window("tab")
    nav.perform_key_combo_chrome(modifier_key, "l")
    nav.clear_awesome_bar()
    nav.context_click_in_awesome_bar()
    nav.context_menu.click_and_hide_menu("context-menu-paste")

    # Wait only for the expected value to appear.
    nav.custom_wait(timeout=20, poll_frequency=1).until(
        lambda _: nav.get_awesome_bar_text() == EXPECTED_URL,
        message=f"Address bar never showed stripped URL {EXPECTED_URL!r}",
    )
