from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = "http://testsafebrowsing.appspot.com/"


@pytest.fixture()
def test_case():
    return "1756779"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.safebrowsing.malware.enabled", True)]


def test_download_malicious_warning(driver: Firefox):
    """
    C1756697 - Verify that the Malicious warning is displayed
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    nav = Navigation(driver)

    # Access the link and download item number 2 from Desktop Download Warnings
    page.open()
    page.click_on("download-malicious-warning")

    # Verify that the "Malicious" message is displayed
    nav.element_visible("malicious-deleted-message")

    # Click on the More Details button (>)
    nav.click_on("download-details-button")

    # Click on Allow download
    nav.click_on("allow-download")
