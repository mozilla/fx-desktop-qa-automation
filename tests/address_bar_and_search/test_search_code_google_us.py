from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation


def test_search_code_google_us(driver: Firefox):
    """
    C1365268 - Default Search Code: Google - US
    This tests multiple ways of sending a search; Awesome bar,
    Search bar and selected text
    """

    nav = Navigation(driver).open()

    # Check code generated from the Awesome bar search
    fx_code = "client=firefox-b-1-d"
    nav.search("soccer")
    WebDriverWait(driver, 10).until(EC.title_contains("Google Search"))
    search_url = driver.current_url
    assert fx_code in search_url
    nav.clear_awesome_bar()

    # Check code generated from the Search bar search

    # Check code generated from the context click of selected text
