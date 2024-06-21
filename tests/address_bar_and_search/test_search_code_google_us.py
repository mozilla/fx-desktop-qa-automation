import time

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
    fx_code = "client=firefox-b-1-d"
    time.sleep(25)
    # Check code generated from the Awesome bar search
    nav.search("soccer")
    WebDriverWait(driver, 10).until(EC.title_contains("Google Search"))
    search_url = driver.current_url
    assert fx_code in search_url
    nav.clear_awesome_bar()
    time.sleep(5)

    # Check code generated from the Search bar search
    # Disabled until ("browser.search.widget.inNavBar", True) is working
    # nav.search_bar_search("soccer")
    # WebDriverWait(driver, 10).until(EC.title_contains("Google Search"))
    # nav.get_awesome_bar()
    # nav.set_content_context()
    # search_url_2 = driver.current_url
    # assert fx_code in search_url_2
    # nav.clear_awesome_bar()

    # Check code generated from the context click of selected text
