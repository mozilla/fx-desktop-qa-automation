import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutDownloads, GenericPage

TEST_URL = "https://sapphire-hendrika-5.tiiny.site/"
DOWNLOAD_FILE_NAME = "sample2.doc"


@pytest.fixture()
def test_case():
    return "2359317"


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
    driver: Firefox,
    panel_ui: PanelUi,
    tabs: TabBar,
    about_downloads: AboutDownloads,
    nav: Navigation,
    delete_files,
):
    """
    C2359317 - Verify that download list is cleared when "End Private Session"
    is used in a Private Window
    """
    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)

    # Open a Private Window
    panel_ui.open_and_switch_to_new_window("private")

    # Download a file
    page.open()
    page.click_on("sample-doc-download")
    nav.click_file_download_warning_panel()
    nav.wait_for_item_to_download(DOWNLOAD_FILE_NAME)

    # Go to about:downloads in a new tab and verify file is displayed
    tabs.new_tab_by_button()
    about_downloads.open()
    assert len(about_downloads.get_downloads()) == 1

    # Click end private session button and verify downloads are cleared
    nav.end_private_session()
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_downloads.open()
    assert about_downloads.is_empty()
