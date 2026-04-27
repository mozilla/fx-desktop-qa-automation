import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi


@pytest.fixture()
def test_case():
    return "216273"


@pytest.fixture()
def use_profile():
    return "theme_change"


@pytest.mark.headed
def test_deleted_page_not_remembered(driver: Firefox, sys_platform):
    """
    C216273: Verify that the deleted page from the Hamburger History
    submenu is not remembered or autofilled in the URL bar
    """
    # Instantiate objects
    panel = PanelUi(driver)
    nav = Navigation(driver)

    # Open history menu and right-click on a specific history entry and delete it
    panel.open_history_menu()
    nav.delete_panel_menu_item_by_title("Firefox Privacy Notice")

    # Type the deleted page name in the URL bar and verify the deleted page is not suggested
    nav.type_in_awesome_bar("Firefox Privacy Notice")
    nav.expect(lambda _: len(nav.get_elements("results-dropdown")) == 1)
