import logging
from time import sleep
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import AboutDownloadsContextMenu, PanelUi, Toolbar
from modules.page_object import AboutDownloads, GenericPage
import pytest

TEST_URL = "https://www.opm.gov/forms/standard-forms/"


@pytest.fixture()
def add_prefs():
    return [("pdfjs.disabled", True)]


def test_downloads_from_private_not_leaked(driver: Firefox):
    """C101674 - Downloads initiated from a private window are not leaked to the non-private window"""

    # We're going to assume no downloads as every test is run in a new instance
    non_private_window = driver.current_window_handle
    panelui = PanelUi(driver).open_panel_menu()
    panelui.select_panel_setting("new-private-window-option")
    panelui.wait_for_num_windows(2)
    panelui.switch_to_new_window()

    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    assert about_downloads.is_empty()

    opm_forms = GenericPage(driver, url=TEST_URL)
    toolbar = Toolbar(driver)
    opm_forms.open()

    links = opm_forms.driver.find_elements("tag name", "a")
    valid_links = [
        el
        for el in links
        if el.get_attribute("href")
        and el.get_attribute("href").endswith(".pdf")
        and el.is_displayed()
    ]
    for link in valid_links[:5]:
        target = link.get_attribute('href')
        logging.info(f"target {target}")
        logging.info(link.text)
        link.click()
        toolbar.wait_for_item_to_download(target.split("/")[-1])

    about_downloads = AboutDownloads(driver)
    context_menu = AboutDownloadsContextMenu(driver)
    about_downloads.open()
    downloads = about_downloads.get_downloads()
    assert len(downloads) == 5

    first_download = downloads[0]
    about_downloads.context_click(first_download)
    assert context_menu.has_all_options_available()
    context_menu.click_and_hide_menu("delete")

    downloads = about_downloads.get_downloads()
    assert len(downloads) == 4

    driver.switch_to.window(non_private_window)
    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    assert about_downloads.is_empty()
