from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


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


@pytest.mark.locale_fr
def test_localized_pocket_layout_FR(driver: Firefox):
    """
    C408038: Test about:blank Pocket layout (ROW / FR)
    """
    tab_bar = TabBar(driver).open()
    tab_bar.new_tab_by_button()
    sleep(4)
