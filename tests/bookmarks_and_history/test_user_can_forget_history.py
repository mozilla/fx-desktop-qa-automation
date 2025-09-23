import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ForgetPanel, Navigation, PanelUi, TabBar
from modules.page_object import CustomizeFirefox, GenericPage


@pytest.fixture()
def test_case():
    return "174072"


ABOUT_PAGES = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
]


def test_user_can_forget_history(driver: Firefox):
    """
    C174072: Verify that the user can Forget all the history from the last 5 minutes
    """
    # Instantiate objects
    tabs = TabBar(driver)
    panel = PanelUi(driver)
    nav = Navigation(driver)
    forget_panel = ForgetPanel(driver)
    customize_firefox = CustomizeFirefox(driver)

    # Add the Forget button to the toolbar
    panel.open_panel_menu()
    panel.navigate_to_customize_toolbar()
    customize_firefox.add_widget_to_toolbar("forget")

    # Create history
    tabs.open_multiple_tabs_with_pages(ABOUT_PAGES)

    # Use Forget button to clear the last 5 minutes of history
    nav.open_forget_panel()
    forget_panel.forget_history("forget-five-minutes")

    # Verify history was removed
    tabs.switch_to_new_tab()
    panel.element_does_not_exist("bookmark-item")
