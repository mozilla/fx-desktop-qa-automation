import sys
from urllib.parse import urlsplit, urlunsplit

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation

SOURCE_URL = "https://www.example.com/?fbclid=1234"


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

    # Open the URL and wait for any canonical redirect to complete.
    driver.get(SOURCE_URL)

    nav.custom_wait(timeout=20, poll_frequency=1).until(
        lambda _: "fbclid=1234" in urlsplit(driver.current_url).query,
        message=(
            "The loaded source URL did not contain the expected tracking parameter. "
            f"Current URL: {driver.current_url!r}"
        ),
    )

    # Build the expected clean URL from the final loaded URL. example.com may
    # redirect www.example.com to example.com depending on the environment.
    loaded_url = urlsplit(driver.current_url)
    expected_url = urlunsplit(
        (
            loaded_url.scheme,
            loaded_url.netloc,
            loaded_url.path or "/",
            "",
            "",
        )
    )

    # Copy the clean link using the Firefox address-bar context menu.
    nav.perform_key_combo_chrome(modifier_key, "l")
    nav.context_click_in_awesome_bar()
    nav.context_menu.click_and_hide_menu("context-menu-copy-clean-link")

    # Paste once in a new tab using the platform-specific keyboard shortcut.
    nav.open_and_switch_to_new_window("tab")
    nav.perform_key_combo_chrome(modifier_key, "l")
    nav.clear_awesome_bar()
    nav.perform_key_combo_chrome(modifier_key, "v")

    pasted_url = None

    def _clean_link_is_pasted(_):
        nonlocal pasted_url
        pasted_url = nav.get_awesome_bar_text()
        return pasted_url == expected_url

    try:
        nav.custom_wait(timeout=20, poll_frequency=1).until(_clean_link_is_pasted)
    except TimeoutException as error:
        raise TimeoutException(
            f"Expected clean URL {expected_url!r}, "
            f"but the address bar contained {pasted_url!r}."
        ) from error
