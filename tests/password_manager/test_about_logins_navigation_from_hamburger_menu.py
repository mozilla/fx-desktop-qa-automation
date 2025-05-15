import pytest
from selenium.webdriver import Firefox
from modules.browser_object import PanelUi, TabBar


ABOUT_LOGINS_PAGE_TITLE = "Passwords"


@pytest.fixture()
def test_case():
    return "2241082"


def test_about_logins_navigation_from_password_hamburger_menu(driver: Firefox):
    """
    C2241082 - Verify that clicking the Password option in Hamburger Menu opens about:logins page in a new tab
    """
    # Instantiate objects
    panel_ui = PanelUi(driver)
    tabs = TabBar(driver)

    # Access Passwords inside the Hamburger Menu
    panel_ui.open_panel_menu()
    panel_ui.redirect_to_about_logins_page()

    # Verify that the about:logins page is opened in a new tab
    tabs.wait_for_num_tabs(2)
    tabs.title_contains(ABOUT_LOGINS_PAGE_TITLE)
