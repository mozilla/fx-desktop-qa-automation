import logging
from time import sleep

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "1618400"


@pytest.mark.slow
def test_preferences_all_toggles_enabled(driver: Firefox):
    """
    C1618400: Preferences - All toggles buttons Enabled
    """
    # instantiate objects
    nav = Navigation(driver)
    driver.implicitly_wait(25)
    about_prefs = AboutPrefs(driver, category="search").open()
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

    # Check if sponsored suggestion is displayed. Using long sleeps otherwise sponsored suggestions won't be displayed
    sleep(20)
    u.search("iphone", with_enter=False)
    with driver.context(driver.CONTEXT_CHROME):
        try:
            nav.get_element("sponsored-suggestion")
        except (NoSuchElementException, TimeoutException):
            u.search("iphone", with_enter=False)
            sleep(20)
        logging.info(
            "Label text:"
            + nav.get_element("sponsored-suggestion").get_attribute("innerText")
        )
        assert any(
            [
                el.get_attribute("innerText") == "Sponsored"
                for el in nav.get_elements("sponsored-suggestion")
            ]
        )

    # Check if a non-sponsored suggestion is displayed
    u.search("wiki", with_enter=False)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("firefox-suggest")
        assert not any(
            [
                el.get_attribute("innerText") == "Sponsored"
                for el in nav.get_elements("sponsored-suggestion")
            ]
        )
