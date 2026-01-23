import time

import pytest
from pynput.keyboard import Controller
from selenium.common import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

APK_URL = (
    "https://www.apkmirror.com/apk/sample-developer/test-dpc/"
    "test-dpc-9-0-13-release/test-dpc-9-0-13-android-apk-download/"
)


@pytest.fixture()
def test_case():
    return "1836830"


@pytest.fixture()
def temp_selectors():
    return {
        "apkmirror-download-apk": {
            "selectorData": "a.downloadButton",
            "strategy": "css",
            "groups": [],
        },
        "apkmirror-accept-cookies": {
            "selectorData": "accept-btn",
            "strategy": "id",
            "groups": [],
        },
    }


@pytest.mark.headed
def test_download_apk_shows_extension_in_downloads_panel(
    driver: Firefox,
    sys_platform,
    temp_selectors,
):
    """
    1836830: Verify the APK filename shown in Firefox Downloads panel includes `.apk`
    """
    page = GenericPage(driver, url=APK_URL)
    nav = Navigation(driver)
    keyboard = Controller()

    # Add temporary page selectors
    page.elements |= temp_selectors

    page.open()
    # Accept cookie consent IF it appears within 3 seconds
    try:
        WebDriverWait(driver, 3).until(
            lambda _: page.get_element("apkmirror-accept-cookies")
        )
        page.click_on("apkmirror-accept-cookies")
    except TimeoutException:
        pass

    # Trigger the download
    page.click_on("apkmirror-download-apk")

    # Confirm native OS save prompt
    time.sleep(2)
    page.handle_os_download_confirmation(keyboard, sys_platform)

    # If Firefox shows the "This file may harm your computer" warning, dismiss it
    # (safe call: it waits/clicks only if present)
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Ensure the downloads UI has time to register an item
    nav.wait_for_download_animation_finish()

    # open panel via click_on so it happens in the chrome context
    nav.element_visible("downloads-button")
    nav.click_on("downloads-button")

    # Now assert what is shown in the Downloads panel UI
    nav.element_visible("download-target-element")
    nav.verify_download_name(r".*\.apk$")
