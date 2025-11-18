import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "1756748"


DOC_LINK = "https://sapphire-hendrika-5.tiiny.site/"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample.*\.doc"


def expected_app_name(sys_platform: str, opt_ci: bool) -> str:
    if sys_platform == "Darwin":
        return "TextEdit" if opt_ci else "Pages"
    return "LibreOffice Writer"


# Test is unstable on Windows GHA because the image does not have a .doc handler
@pytest.mark.noxvfb
def test_mime_type_doc(driver: Firefox, sys_platform: str, opt_ci: bool, delete_files):
    """
    C1756748 - Verify that downloading a .doc file adds a new MIME type entry
    and the correct default application is assigned.
    """

    # Instantiate objects
    page = GenericPage(driver, url=DOC_LINK)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Open the test page with the .doc download link
    page.open()
    page.click_on("sample-doc-download")

    # Download the file and set 'Always Open Similar Files'
    nav.set_always_open_similar_files()

    # Verify the MIME type entry exists and default app matches expectation
    about_prefs.open()
    app_name = about_prefs.get_app_name_for_mime_type("application/msword")
    assert app_name == expected_app_name(sys_platform, opt_ci)
