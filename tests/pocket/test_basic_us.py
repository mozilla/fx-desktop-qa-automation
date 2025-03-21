import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNewtab


@pytest.fixture()
def test_case():
    return "408037"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.ping-centre.log", True),
        (
            "browser.newtabpage.activity-stream.discoverystream.spocs-endpoint",
            "https://spocs.getpocket.com/spocs?country=US&region=CA",
        ),
    ]


@pytest.mark.skip(reason="Pocket tests no longer belong to DTE.")
def test_new_tab_about_blank(driver: Firefox):
    """
    C408037: Test about:blank Pocket layout (US). First step only.
    """
    tab_bar = TabBar(driver)
    tab_bar.new_tab_by_button()
    assert driver.current_url == "about:blank"


# LOW PRIORITY
@pytest.mark.skip(reason="Pocket tests no longer belong to DTE.")
def test_localized_pocket_layout_US(driver: Firefox, screenshot):
    """
    C408037: Test about:blank Pocket layout (US)
    """
    about_newtab = AboutNewtab(driver).open()
    about_newtab.set_language_code("enUS")
    about_newtab.check_layout()
