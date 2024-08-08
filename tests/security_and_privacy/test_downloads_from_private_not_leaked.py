import logging
import os

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AboutDownloadsContextMenu, PanelUi, Toolbar
from modules.page_object import AboutDownloads, GenericPage

TEST_URL = "https://www.opm.gov/forms/opm-forms/"
NUM_LINKS = 3


@pytest.fixture()
def add_prefs():
    return [("pdfjs.disabled", True)]


@pytest.fixture()
def delete_files(sys_platform):
    """Remove the files after the test finishes, should work for Mac/Linux/MinGW"""

    def _delete_files():
        if sys_platform.startswith("Win"):
            if os.environ.get("GITHUB_ACTIONS") == "true":
                downloads_folder = os.path.join(
                    "C:", "Users", "runneradmin", "Downloads"
                )
        else:
            home_folder = os.environ.get("HOME")
            downloads_folder = os.path.join(home_folder, "Downloads")
        for file in os.listdir(downloads_folder):
            if file.startswith("opm") and file.endswith("pdf"):
                os.remove(os.path.join(downloads_folder, file))

    _delete_files()
    yield True
    _delete_files()


@pytest.mark.slow
def test_downloads_from_private_not_leaked(driver: Firefox, delete_files, screenshot):
    """C101674 - Downloads initiated from a private window are not leaked to the non-private window"""

    # We've deleted relevant downloads_file just to be safe
    non_private_window = driver.current_window_handle
    panelui = PanelUi(driver).open_panel_menu()
    panelui.select_panel_setting("new-private-window-option")
    panelui.wait_for_num_windows(2)

    # Using this instead of switch_to_new_window, suspect it may be broken
    original_window_idx = driver.window_handles.index(non_private_window)
    private_window = driver.window_handles[1 - original_window_idx]
    driver.switch_to.window(private_window)

    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    if not about_downloads.is_empty():
        screenshot("about_downloads_not_empty")
        logging.warning("About:Downloads is not registering as empty")

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
