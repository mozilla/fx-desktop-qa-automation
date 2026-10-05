from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

# The locale segment is present for some add-ons and absent for others.
ADDONS_URL_PATTERN = r"addons\.mozilla\.org/(\w\w-\w\w/)?firefox/addon/{}/"

INPUT_TO_ADDON = {
    "video download": ("Video DownloadHelper", "video-downloadhelper"),
    "grammar": ("LanguageTool", "languagetool"),
    "alias": ("Firefox Relay", "private-relay"),
    "image finder": ("Search by Image", "search_by_image"),
    "darker theme": ("Dark Reader", "darkreader"),
    "accessibility reader": ("Read Aloud", "read-aloud"),
}


@pytest.fixture()
def test_case():
    return "3029292"


@pytest.fixture()
def add_to_prefs_list():
    """Pin the Firefox Suggest add-on suggestion feature on."""
    return [
        ("browser.urlbar.quicksuggest.enabled", True),
        ("browser.urlbar.suggest.quicksuggest.nonsponsored", True),
        ("browser.urlbar.addons.featureGate", True),
        ("browser.urlbar.suggest.addons", True),
    ]


@pytest.mark.noxvfb
def test_addon_suggestion_based_on_search_input(driver: Firefox):
    """
    C3029292 - Verify that the address bar suggests relevant add-ons based on search input.
    """
    nav = Navigation(driver)

    sleep(3)  # Wait for Firefox to do backend addons initiation

    for input_text, (addon_name, addon_slug) in INPUT_TO_ADDON.items():
        driver.get("about:newtab")
        nav.set_awesome_bar()
        nav.type_in_awesome_bar(input_text)

        nav.element_visible("addon-suggestion")
        nav.element_has_text("addon-suggestion-title", addon_name)

        nav.select_element_in_nav("addon-suggestion")
        nav.expect_in_content(EC.url_matches(ADDONS_URL_PATTERN.format(addon_slug)))
