import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ForgetPanel, Navigation, PanelUi, TabBar
from modules.page_object import CustomizeFirefox, GenericPage


@pytest.fixture()
def test_case():
    return "174072"

links = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
]


def test_user_can_forget_history(driver: Firefox):
    """
    C174072: Verify that the user can Forget all the history from the last 5 minutes
    """
    tabs = TabBar(driver).open()
    panel_ui = PanelUi(driver)
    nav = Navigation(driver)
    forget_panel = ForgetPanel(driver)
    gen_page = GenericPage(driver, url="https://www.google.com/")
    customize_firefox = CustomizeFirefox(driver)

    tabs_to_open = 4

    for i in range(tabs_to_open):
        driver.get(links[i])
        tabs.new_tab_by_button()
        tabs.switch_to_new_tab()

    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize_firefox.add_widget_to_toolbar("forget")

    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    gen_page.open()

    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("forget-button").click()
        assert (
            forget_panel.get_element("forget-five-minutes").get_attribute("selected")
            == "true"
        )

    forget_panel.forget_history("forget-five-minutes")

    tabs.switch_to_new_tab()
    panel_ui.element_does_not_exist("recent-history-info")
