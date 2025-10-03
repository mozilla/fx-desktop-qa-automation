import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar


URL = "about:robots"
EXPECTED_TEXT = "Firefox"


@pytest.fixture()
def test_case():
    return "134453"


def test_open_new_tab_plus(driver: Firefox):
    """
    C134453 - A new tab can be opened from the dedicated button ("+")
    """

    # Instantiate object
    browser = TabBar(driver)

    # Open page and check a new tab can be opened from the dedicated button ("+")
    driver.get(URL)
    browser.set_chrome_context()
    browser.new_tab_by_button()
    browser.expect(EC.title_contains(EXPECTED_TEXT))
    assert EXPECTED_TEXT in driver.title, (
        f"Expected title to contain 'Firefox', but got '{driver.title}'"
    )
