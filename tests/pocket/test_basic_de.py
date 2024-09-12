import pytest
from selenium.webdriver import Firefox

from modules.page_object import NewTab


@pytest.fixture()
def test_case():
    return "469597"


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "DE"),
        ("browser.ping-centre.log", True),
    ]


# LOW PRIORITY
@pytest.mark.unstable
@pytest.mark.locale_de
def test_localized_pocket_layout_DE(driver: Firefox):
    """
    C469597: Test about:blank Pocket layout (DE)
    """
    about_newtab = NewTab(driver).open()
    about_newtab.set_language_code("deDE")
    about_newtab.check_layout()
