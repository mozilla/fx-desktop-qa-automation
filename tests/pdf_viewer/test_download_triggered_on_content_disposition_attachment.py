from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_prefs import AboutPrefs

CONTENT_DISPOSITION_ATTACHMENT_URL = (
    "https://download.novapdf.com/download/samples/pdf-example-bookmarks.pdf"
)


def test_download_panel_triggered_on_content_disposition_attachment(driver: Firefox):
    """
    C936502: Ensure that the Always ask option in Firefox Applications settings
    triggers the download panel for PDFs with Content-Disposition: attachment.
    """

    tabs = TabBar(driver)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general").open()

    about_prefs.find_in_settings("appl")
    about_prefs.click_on("pdf-content-type")
    about_prefs.click_on("pdf-actions-menu")
    menu = about_prefs.get_element("pdf-actions-menu")
    menu.send_keys(Keys.DOWN)
    menu.send_keys(Keys.ENTER)
    about_prefs.wait.until(lambda _: menu.get_attribute("label") == "Always ask")

    nav.search(CONTENT_DISPOSITION_ATTACHMENT_URL)
    sleep(3)
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        driver.find_element(By.ID, "handleInternally").click()
        sleep(2)
        driver.find_element(By.ID, "unknownContentTypeWindow").send_keys(Keys.ENTER)

    tabs.wait_for_num_tabs(2)
    assert (
        len(driver.window_handles) == 2
    ), f"Expected 2 tabs, but found {len(driver.window_handles)}"

    tabs.switch_to_new_tab()
    assert driver.current_url.startswith(
        "file://"
    ), "Expected URL to start with 'file://'"
