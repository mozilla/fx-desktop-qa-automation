import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar, ContextMenu
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134444"


def test_open_new_via_hyperlink(driver: Firefox):
    """
    C134444 - A hyperlink can be opened in a new tab
    """
    browser = TabBar(driver)
    example = ExamplePage(driver).open()

    # Use context menu option to open link in new tab
    example.context_click("more-information")
    context_menu = ContextMenu(driver)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.click_and_hide_menu("context-menu-open-link-in-tab")

    # Get the title of the new tab
    example.wait_for_num_tabs(2)
    example.switch_to_new_tab()
    example.url_contains("https://www.iana.org/domains/example")
