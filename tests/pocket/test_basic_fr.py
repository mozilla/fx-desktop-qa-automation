import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutNewtab


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "FR"),
        ("browser.ping-centre.log", True),
    ]


@pytest.mark.unstable
@pytest.mark.locale_fr
def test_localized_pocket_layout_FR(driver: Firefox):
    """
    C408038: Test about:blank Pocket layout (ROW / FR)
    """
    about_newtab = AboutNewtab(driver).open()
    about_newtab.set_language_code("frFR")
    about_newtab.check_layout()
