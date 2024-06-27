from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


def test_addon_suggestion_based_on_search_input(driver: Firefox):
    """
    C2234714: Test that add-on suggestions match the URL bar input.
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

    driver.get("about:addons")
    nav = Navigation(driver)
    nav.set_awesome_bar()
    nav.awesome_bar.click()
    for input_text, addon_name in input_to_addon_name.items():
        for _ in range(3):
            nav.awesome_bar.send_keys(input_text)
            if nav.get_elements("addon-suggestion"):
                nav.get_element("addon-suggestion").click()
                break
            else:
                nav.clear_awesome_bar()
                with driver.context(driver.CONTEXT_CONTENT):
                    driver.find_element("tag name", "body").click()

        # Construct the expected URL
        expected_url = f"https://addons.mozilla.org/en-US/firefox/addon/{addon_name}/"
        nav.expect_in_content(EC.url_contains(expected_url))
        nav.clear_awesome_bar()
