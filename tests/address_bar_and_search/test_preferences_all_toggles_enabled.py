import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "1618400"


def test_preferences_all_toggles_enabled(driver: Firefox):
    """
    C1618400: Preferences - All toggles buttons Enabled
    """
    # instantiate objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="search")
    about_prefs.open()
    u = BrowserActions(driver)

    # Check if toggles are enabled
    show_suggestions_checkbox = about_prefs.get_element("show-suggestions")
    if not show_suggestions_checkbox.is_selected():
        show_suggestions_checkbox.click()
    nonsponsored_checkbox = about_prefs.get_element("firefox-suggest-nonsponsored")
    assert (
        nonsponsored_checkbox.is_selected()
    ), f"Checkbox with selector '{nonsponsored_checkbox}' is not checked"
    sponsors_checkbox = about_prefs.get_element("firefox-suggest-sponsored")
    assert (
        sponsors_checkbox.is_selected()
    ), f"Checkbox with selector '{sponsors_checkbox}' is not checked"

    # Check if sponsored suggestion is displayed. Keep checking until the sponsered suggestions are displayed
    found = False
    retries = 0
    while not found and retries < 20:
        u.search("iphone", with_enter=False)
        with driver.context(driver.CONTEXT_CHROME):
            found = any(
                [
                    el.get_attribute("innerText") == "Sponsored"
                    for el in nav.get_elements("sponsored-suggestion")
                ]
            )
            logging.info(
                "Label text:"
                + nav.get_element("sponsored-suggestion").get_attribute("innerText")
            )
        sleep(3)
        retries += 1

    # Check if a non-sponsored suggestion is displayed
    u.search("wiki", with_enter=False)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("firefox-suggest")
        nav.get_element("sponsored-suggestion")
        assert not any(
            [
                el.get_attribute("innerText") == "Sponsored"
                for el in nav.get_elements("sponsored-suggestion")
            ]
        )
