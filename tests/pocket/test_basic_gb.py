import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutNewtab


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "GB"),
        ("browser.ping-centre.log", True),
    ]


# LOW PRIORITY
@pytest.mark.unstable
@pytest.mark.locale_gb
def test_localized_pocket_layout_GB(driver: Firefox):
    """
    C559390: Test about:blank Pocket layout (GB)
    """
    about_newtab = AboutNewtab(driver).open()
    about_newtab.set_language_code("enGB")
    about_newtab.check_layout()
