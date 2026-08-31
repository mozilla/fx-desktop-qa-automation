from subprocess import run
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "4108461"


DOC_LINK = "https://sapphire-hendrika-5.tiiny.site/"
HANDLER_LAUNCH_SEC = 5
HANDLER_CLOSE_SEC = 2


@pytest.fixture()
def delete_files_regex_string():
    return r"sample.*\.doc"


@pytest.fixture()
def close_doc_handler(sys_platform):
    """Quit the app the OS opens the downloaded .doc in."""
    yield
    # Let the handler finish launching, or it opens onto a deleted file
    sleep(HANDLER_LAUNCH_SEC)
    if sys_platform == "Darwin":
        for app in ("TextEdit", "Pages", "Microsoft Word"):
            # The `is running` guard stops osascript launching the app
            run(
                [
                    "osascript",
                    "-e",
                    f'if application "{app}" is running then '
                    f'tell application "{app}" to quit saving no',
                ],
                check=False,
            )
    elif sys_platform == "Linux":
        run(["pkill", "-f", "soffice"], check=False)
    elif sys_platform == "Windows":
        run(["taskkill", "/F", "/T", "/IM", "WINWORD.EXE"], check=False)
    # Windows keeps the file locked briefly after the app dies.
    sleep(HANDLER_CLOSE_SEC)


@pytest.mark.noxvfb
def test_mime_type_doc(driver: Firefox, delete_files, close_doc_handler):
    """
    C4108461 - Verify that downloading a .doc file adds the .doc MIME type
    entry to the Files and Applications list.
    """

    # Instantiate objects
    page = GenericPage(driver, url=DOC_LINK)
    nav = Navigation(driver)
    # The settings redesign (bug 2043378) moved file handlers to this pane
    about_prefs = AboutPrefs(driver, category="downloads")

    # Open the test page with the .doc download link
    page.open()
    page.click_on("sample-doc-download")

    # Download the file and set 'Always Open Similar Files'
    nav.perform_download_context_action("context-menu-always-open-similar-files")

    # Check the doc mime type is listed. Its label and app come from the OS
    about_prefs.open()
    about_prefs.element_exists("mime-type-item", labels=["application/msword"])
