import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import AboutDownloadsContextMenu, PanelUi, Toolbar
from modules.page_object import AboutDownloads, GenericPage

TEST_URL = "https://www.opm.gov/forms/opm-forms/"
NUM_LINKS = 3


@pytest.fixture()
def add_prefs():
    return [("pdfjs.disabled", True)]


@pytest.mark.slow
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

    # Get all links to pdfs on the page
    links = opm_forms.driver.find_elements("tag name", "a")
    valid_links = [
        el
        for el in links
        if el.get_attribute("href")
        and el.get_attribute("href").endswith(".pdf")
        and el.is_displayed()
    ]
    # first link is large, skip it
    for link in valid_links[1 : (NUM_LINKS + 1)]:
        target = link.get_attribute("href")
        logging.info(f"Downloading target {target}:")
        logging.info(link.text)
        link.click()
        toolbar.wait_for_item_to_download(target.split("/")[-1])

    # Check that everything looks good in About:Downloads
    about_downloads = AboutDownloads(driver)
    context_menu = AboutDownloadsContextMenu(driver)
    about_downloads.open()
    about_downloads.wait_for_num_downloads(NUM_LINKS)
    downloads = about_downloads.get_downloads()
    assert len(downloads) == NUM_LINKS

    first_download = downloads[0]
    about_downloads.context_click(first_download)

    # We are not testing all the context menu options, that should be a test in another suite
    context_menu.click_and_hide_menu("delete")
    about_downloads.expect(
        lambda _: (
            about_downloads.get_parent_of(first_download)
            .find_element("class name", "downloadDetails")
            .get_attribute("value")
            .startswith("File deleted")
        )
    )

    # Check that nothing has leaked
    driver.switch_to.window(non_private_window)
    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    assert about_downloads.is_empty()
