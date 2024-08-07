from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_prefs import AboutPrefs

CONTENT_DISPOSITION_ATTACHMENT_URL = (
    "https://download.novapdf.com/download/samples/pdf-example-bookmarks.pdf"
)


@pytest.mark.headed
def test_download_panel_triggered_on_content_disposition_attachment(driver: Firefox):
    """
    C936502: Ensure that the "Always ask" option in Firefox Applications settings
    triggers the download panel for PDFs with Content-Disposition: attachment.
    """

    from pynput.keyboard import Controller, Key

    keyboard = Controller()
    tabs = TabBar(driver)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general").open()

    about_prefs.get_element("pdf-content-type").click()
    about_prefs.get_element("pdf-open-in-firefox").click()
    sleep(3)
    keyboard.press(Key.down)
    keyboard.press(Key.enter)

    nav.search(CONTENT_DISPOSITION_ATTACHMENT_URL)
    sleep(3)
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])

        driver.find_element(By.ID, "handleInternally").click()
        keyboard.press(Key.enter)

    tabs.wait_for_num_tabs(2)
    assert (
        len(driver.window_handles) == 2
    ), f"Expected 2 tabs, but found {len(driver.window_handles)}"

    tabs.switch_to_new_tab()
    assert driver.current_url.startswith(
        "file://"
    ), "Expected URL to start with 'file://'"
