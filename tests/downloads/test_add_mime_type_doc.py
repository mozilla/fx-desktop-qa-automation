import subprocess

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "1756748"


# Constants
DOC_LINK = "https://sapphire-hendrika-5.tiiny.site/"
# WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.fixture()
def delete_files_regex_string():
    return r"sample.*\.doc"


def expected_app_name(sys_platform: str, opt_ci: bool) -> str:
    """
    Decide which default application should be used to open .doc files, based on OS and CI environment
    """
    if sys_platform == "Darwin":
        return "TextEdit" if opt_ci else "Pages"
    # Linux/Windows
    return "LibreOffice Writer"


@pytest.mark.noxvfb
# @pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
def test_mime_type_doc(driver: Firefox, sys_platform: str, opt_ci: bool, delete_files):
    """
    C1756748 - Verify that downloading a .doc file adds a new MIME type entry
    and the correct default application is assigned.
    """
    # Instantiate objects
    page = GenericPage(driver, url=DOC_LINK)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general")
    tabs = TabBar(driver)

    # Open the test page with the .doc download link
    page.open()
    page.click_on("sample-doc-download")

    # Download the file and set 'Always Open Similar Files'
    nav.set_always_open_similar_files()

    # Verify the MIME type entry exists and default app matches expectation
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_prefs.open()
    app_name = about_prefs.get_app_name_for_mime_type("application/msword")
    assert app_name == expected_app_name(sys_platform, opt_ci)

    # Kill LibreOffice before cleanup to prevent file lock
    if sys_platform == "Windows":
        subprocess.run(
            ["taskkill", "/F", "/IM", "soffice.bin"], capture_output=True, check=False
        )
        subprocess.run(
            ["taskkill", "/F", "/IM", "soffice.exe"], capture_output=True, check=False
        )
