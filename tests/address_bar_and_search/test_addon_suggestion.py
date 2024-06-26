import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

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


@pytest.mark.parametrize("input_text, addon_name", input_to_addon_name.items())
def test_addon_suggestion_based_on_search_input(
    driver: Firefox, input_text: str, addon_name: str
):
    """
    C2234714: Test that add-on suggestions match the URL bar input.
    """

    nav = Navigation(driver).open()
    time.sleep(10)
    nav.set_awesome_bar()
    time.sleep(10)
    nav.awesome_bar.click()
    nav.awesome_bar.send_keys(input_text)
    nav.element_visible("addon-suggestion")
    nav.get_element("addon-suggestion").click()

    # Construct the expected URL
    expected_url = f"https://addons.mozilla.org/en-US/firefox/addon/{addon_name}/"
    nav.expect_in_content(EC.url_contains(expected_url))
