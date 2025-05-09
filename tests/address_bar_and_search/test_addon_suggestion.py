import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

WAIT_TIMEOUT = 10
ADDONS_BASE_URL = "https://addons.mozilla.org/en-US/firefox/addon/"

INPUT_TO_ADDON_NAME = {
    "clips": "video-downloadhelper",
    "grammar": "languagetool",
    "Temp mail": "private-relay",
    "pics search": "search_by_image",
    "darker theme": "darkreader",
    "privacy": "privacy-badger17",
    "read aloud": "read-aloud",
}


@pytest.fixture()
def test_case():
    return "3029292"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.urlbar.suggest.addons", True),
        ("browser.urlbar.addons.featureGate", True),
    ]


def test_addon_suggestion_based_on_search_input(driver: Firefox):
    """
    C2234714 - Verify that the address bar suggests relevant add-ons based on search input.
    """
    nav = Navigation(driver)
    nav.set_awesome_bar()

    for input_text, addon_slug in INPUT_TO_ADDON_NAME.items():
        nav.type_in_awesome_bar(input_text)

        if not nav.element_visible("addon-suggestion"):
            raise AssertionError(
                f"Addon suggestion not visible for input: '{input_text}'"
            )

        nav.select_element_in_nav("addon-suggestion")
        expected_url = f"{ADDONS_BASE_URL}{addon_slug}/"
        nav.expect_in_content(EC.url_contains(expected_url))
        nav.clear_awesome_bar()
