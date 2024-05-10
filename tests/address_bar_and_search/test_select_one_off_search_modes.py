import pytest
from selenium.webdriver import Firefox
from modules.browser_object import Navigation

# One-off search engine names and the corresponding urlbar
# search shard aren't always identical text
sites = [("Google","Google"),
         ("Amazon", "Amazon.com"),
         ("Bing", "Bing"),
         ("DuckDuckGo", "DuckDuckGo"),
         ("eBay", "eBay"),
         ("Wikipedia", "Wikipedia (en)")]


@pytest.mark.parametrize("engine, shard", sites)
def test_select_search_engine_modes(driver: Firefox, engine: str, shard: str):
    # C?????? TestRail test unknown
    nav = Navigation(driver).open()

    # Select a one-off search engine
    nav.set_awesome_bar()
    nav.awesome_bar.click()
    nav.get_element("search-one-off-engine-button", engine).click()

    # Check that the urlbar search engine shard is correct
    chip_text = nav.get_element("search-mode-span").get_attribute("innerText")
    assert chip_text == shard
    nav.clear_awesome_bar()