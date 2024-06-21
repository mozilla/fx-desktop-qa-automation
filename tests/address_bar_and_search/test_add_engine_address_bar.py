from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation


def test_add_search_engine_from_address_bar(driver: Firefox):
    """
    C1365478: Test that an open search engine can be added from the address bar.
    """

    site = "YouTube"
    nav = Navigation(driver).open()
    nav.search("youtube.com")
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.youtube.com"))
    nav.click_in_awesome_bar()
    nav.element_clickable("add-extra-search-engine", labels=[site])
    nav.get_element("add-extra-search-engine", labels=[site]).click()
    nav.get_element("search-one-off-engine-button", labels=[site]).click()
    nav.search("soccer")
    nav.expect_in_content(EC.url_contains("youtube"))
