from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutConfig
from modules.page_object_generics import GenericPage

TEST_URL = "http://testsafebrowsing.appspot.com/"


@pytest.fixture()
def test_case():
    return "1756779"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.safebrowsing.malware.enabled", True),
        ("browser.safebrowsing.downloads.enabled", True),
        ("browser.aboutConfig.showWarning", False)
    ]


def test_download_malicious_warning(driver: Firefox):
    """
    C1756697 - Verify that the Malicious warning is displayed
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    nav = Navigation(driver)
    about_config = AboutConfig(driver)

    # Access the link and download item number 2 from Desktop Download Warnings
    page.open()
    page.click_on("download-malicious-warning")

    # Verify that the "Malicious" message is displayed
    nav.element_visible("download-malicious-message")

    # Click on the More Details button (>)
    nav.click_on("download-details-button")

    # Click on remove download
    nav.click_on("remove-download")

    # Check that the file is deleted from the Panel
    assert not nav.is_download_button_visible()

    # Repeat steps 1-4 and click on allow file
    page.click_on("download-malicious-warning")
    nav.click_on("download-details-button")
    nav.click_on("allow-download")
    assert nav.is_download_button_visible()

    # Set browser.download.alwaysOpenPanel to False and repeat step 2
    about_config.toggle_config_value("browser.download.alwaysOpenPanel", False)

    # Check the Download Panel is not opened and the red warning is displayed on toolbar Downloads icon
    page.open()
    page.click_on("download-malicious-warning")
    sleep(2)
    assert nav.is_download_warning_button_visible()
