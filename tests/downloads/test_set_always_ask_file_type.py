import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "4108462"


def test_set_always_ask_file_type(driver: Firefox, fillable_pdf_url: str):
    """
    C4108462 - Verify that setting PDF handling to "Always ask" makes a PDF
    download show the "What should Firefox do with this file?" dialog.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    # The settings redesign (bug 2043378) moved file handlers to this pane
    about_prefs = AboutPrefs(driver, category="downloads")

    # Set PDF handling to "Always ask"
    about_prefs.open()
    about_prefs.set_pdf_handling_to_always_ask()

    # Download the PDF again from a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    nav.search(fillable_pdf_url)

    # The dialog opens in its own window, Escape cancels out of it
    about_prefs.handle_unknown_content_dialog()
