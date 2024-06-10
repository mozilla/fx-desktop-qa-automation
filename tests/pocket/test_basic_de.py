import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutBlank


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "DE"),
        ("browser.ping-centre.log", True),
    ]


@pytest.mark.locale_de
def test_localized_pocket_layout_DE(driver: Firefox):
    """
    C469597: Test about:blank Pocket layout (DE)
    """
    tab_bar = TabBar(driver).open()
    tab_bar.new_tab_by_button()

    driver.switch_to.window(driver.window_handles[-1])
    about_blank = AboutBlank(driver)
    about_blank.set_language_code("deDE")
    about_blank.check_layout()
