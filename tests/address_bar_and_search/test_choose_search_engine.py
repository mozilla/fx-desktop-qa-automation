import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from modules.browser_object import Navigation
from modules.page_object import GenericPage

engines = ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay", "Wikipedia"]

@pytest.fixture()
def test_case():
    return "mystery number"

@pytest.mark.unsure
@pytest.mark.parametrize("engine", engines)
def test_choose_search_engine(driver: Firefox, engine: str):
    # instantiate objects
    nav = Navigation(driver).open()
    page = GenericPage(driver, url="")

    # type in awesome bar so dropdown menu appears
    nav.type_in_awesome_bar("hello")
    nav.change_search_engine_once(engine)
    nav.type_in_awesome_bar(Keys.ENTER)
    page.url_contains(engine.lower())
    