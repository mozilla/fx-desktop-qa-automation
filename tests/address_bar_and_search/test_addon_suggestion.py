import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from modules.browser_object import Navigation

ADDONS_BASE_URL = "https://addons.mozilla.org/en-US/firefox/addon/"
AWESOME_BAR_SELECTOR = "addon-suggestion"
WAIT_TIMEOUT = 10


@pytest.fixture()
def test_case():
    return "2234714"


def test_addon_suggestion_based_on_search_input(driver: Firefox):
    """
    C2234714 - Verify that the address bar suggests relevant add-ons based on search input.
    """
    input_to_addon_name = {
        "clips": "video-downloadhelper",
        "grammar": "languagetool",
        "Temp mail": "private-relay",
        "pics search": "search_by_image",
        "darker theme": "darkreader",
        "privacy": "privacy-badger17",
        "read aloud": "read-aloud",
    }

    nav = Navigation(driver)
    nav.set_awesome_bar()
    WebDriverWait(driver, WAIT_TIMEOUT).until(lambda d: True)

    for input_text, addon_name in input_to_addon_name.items():
        nav.type_in_awesome_bar(input_text)
        try:
            nav.element_visible(AWESOME_BAR_SELECTOR)
        except TimeoutException:
            raise AssertionError(f"Addon suggestion not visible for input: '{input_text}'")

        nav.select_element_in_nav(AWESOME_BAR_SELECTOR)

        expected_url = f"{ADDONS_BASE_URL}{addon_name}/"
        nav.expect_in_content(EC.url_contains(expected_url))

        nav.clear_awesome_bar()
