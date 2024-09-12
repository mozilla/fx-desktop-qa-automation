import pytest
from selenium.webdriver import Firefox

from modules.page_object import NewTab


@pytest.fixture()
def test_case():
    return "408038"


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "FR"),
        ("browser.ping-centre.log", True),
    ]


# LOW PRIORITY
@pytest.mark.unstable
@pytest.mark.locale_fr
def test_localized_pocket_layout_FR(driver: Firefox):
    """
    C408038: Test about:blank Pocket layout (ROW / FR)
    """
    about_newtab = NewTab(driver).open()
    about_newtab.set_language_code("frFR")
    about_newtab.check_layout()
