import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutDownloads
from modules.page_object_generics import GenericPage

TEST_URL = "https://sapphire-hendrika-5.tiiny.site/"
DOWNLOAD_FILE_NAME = "sample2.doc"


@pytest.fixture()
def test_case():
    return "2359320"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


@pytest.fixture()
def delete_files_regex_string():
    return r"sample2.*\.doc"


def test_download_list_is_cleared_by_end_private_session_button(
    driver: Firefox, delete_files
):
    """
    C2359320 - Verify that download list is cleared when "End Private Session" is used in a Private Window
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)
    page = GenericPage(driver, url=TEST_URL)
    about_downloads = AboutDownloads(driver)

    # Open a Private Window
    panel.open_and_switch_to_new_window("private")

    # Download a file
    page.open()
    page.click_on("sample-doc-download")
    nav.click_file_download_warning_panel()
    nav.wait_for_item_to_download(DOWNLOAD_FILE_NAME)

    # Go to about:downloads in a new tab and verify file is displayed
    tabs.new_tab_by_button()
    about_downloads.open()
    about_downloads.wait_for_num_downloads(1)
    downloads = about_downloads.get_downloads()
    assert len(downloads) == 1

    # Click end private session button and verify downloads are cleared
    nav.end_private_session()
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_downloads.open()
    assert about_downloads.is_empty()
