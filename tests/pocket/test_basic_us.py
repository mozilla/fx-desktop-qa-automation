import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNewtab


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
        ("browser.ping-centre.log", True),
        (
            "browser.newtabpage.activity-stream.discoverystream.spocs-endpoint",
            "https://spocs.getpocket.com/spocs?country=US&region=CA",
        ),
    ]


def test_new_tab_about_blank(driver: Firefox):
    """
    C408037: Test about:blank Pocket layout (US). First step only.
    """
    tab_bar = TabBar(driver).open()
    tab_bar.new_tab_by_button()
    assert driver.current_url == "about:blank"


# LOW PRIORITY
@pytest.mark.unstable
def test_localized_pocket_layout_US(driver: Firefox, screenshot):
    """
    C408037: Test about:blank Pocket layout (US)
    """
    about_newtab = AboutNewtab(driver).open()
    about_newtab.set_language_code("enUS")
    about_newtab.check_layout()
