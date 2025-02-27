import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object_context_menu import AboutDownloadsContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object import AboutDownloads, GenericPage


@pytest.fixture()
def test_case():
    return "101674"


TEST_URL = "https://www.opm.gov/forms/opm-forms/"
NUM_LINKS = 3


@pytest.fixture()
def add_prefs():
    return [("pdfjs.disabled", True)]


@pytest.fixture()
def delete_files_regex_string():
    return r"opm.*\.pdf"


@pytest.mark.slow
@pytest.mark.audio
def test_downloads_from_private_not_leaked(driver: Firefox, delete_files, screenshot):
    """C101674 - Downloads initiated from a private window are not leaked to the non-private window"""

    # We've deleted relevant downloads_file just to be safe
    non_private_window = driver.current_window_handle
    panel_ui = PanelUi(driver)
    nav = Navigation(driver)

    panel_ui.open_and_switch_to_new_window("private")

    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    if not about_downloads.is_empty():
        screenshot("about_downloads_not_empty")
        logging.warning("About:Downloads is not registering as empty")

    opm_forms = GenericPage(driver, url=TEST_URL)
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
        nav.wait_for_item_to_download(target.split("/")[-1])

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
    context_menu.has_all_options_available()
    context_menu.click_and_hide_menu("delete")
    about_downloads.expect(
        lambda _: (
            about_downloads.get_parent_of(first_download)
            .find_element("class name", "downloadDetails")
            .get_attribute("value")
            .startswith("File deleted")
        )
    )

    script = 'document.querySelector("#downloadsContextMenu").hidePopup();'
    with driver.context(driver.CONTEXT_CONTENT):
        driver.execute_script(script)

    # Check that nothing has leaked
    driver.switch_to.window(non_private_window)
    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    assert about_downloads.is_empty()
