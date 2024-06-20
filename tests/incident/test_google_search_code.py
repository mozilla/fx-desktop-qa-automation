import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation


@pytest.mark.incident
def test_google_search_code(driver: Firefox):
    """
    C1365268 - Default Search Code: Google - US
    Only tests the Awesome bar portion of the test for Incident smoke
    """

    nav = Navigation(driver).open()

    # Check code generated from the Awesome bar search
    fx_code = "client=firefox-b-1-d"
    nav.search("soccer")
    WebDriverWait(driver, 10).until(EC.title_contains("Google Search"))
    search_url = driver.current_url
    assert fx_code in search_url
    nav.clear_awesome_bar()
