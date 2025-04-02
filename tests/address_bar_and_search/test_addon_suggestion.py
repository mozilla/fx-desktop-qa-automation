from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2234714"


@pytest.mark.xfail(
    reason="Firefox bug https://bugzilla.mozilla.org/show_bug.cgi?id=1958038"
)
def test_addon_suggestion_based_on_search_input(driver: Firefox):
    """
    C2234714: Test that add-on suggestions match the URL bar input.

    To avoid lengthy waits caused by network traffic during browser startup,
    this test loops through the list of addons in a single browser session
    instead of using parameterization. This reduces the overall test duration
    by waiting for the network traffic only once.
    """

    # Map input text to addon names
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
    sleep(2)

    for input_text, addon_name in input_to_addon_name.items():
        nav.type_in_awesome_bar(input_text)
        nav.element_visible("addon-suggestion")
        nav.select_element_in_nav("addon-suggestion")

        # Construct the expected URL
        expected_url = f"https://addons.mozilla.org/en-US/firefox/addon/{addon_name}/"
        nav.expect_in_content(EC.url_contains(expected_url))
        nav.clear_awesome_bar()
