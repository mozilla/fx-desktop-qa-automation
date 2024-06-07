from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "GB"),
        ("browser.ping-centre.log", True),
    ]


def test_localized_pocket_layout_GB(driver: Firefox):
    """
    C559390: Test about:blank Pocket layout (GB)
    """
    tab_bar = TabBar(driver).open()
    tab_bar.new_tab_by_button()
    sleep(4)
