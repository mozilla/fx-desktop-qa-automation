import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

# Dict that maps the site to the string to verify
search_with_engines_map = {
    "Google": "Google",
    "Amazon": "Amazon.com",
    "Bing": "Bing",
    "DuckDuckGo": "DuckDuckGo",
    "eBay": "eBay",
    "Wikipedia": "Wikipedia (en)",
}


@pytest.mark.parametrize("engine", search_with_engines_map.keys())
def test_search_with_buttons(driver: Firefox, engine: str):
    engine_shard = search_with_engines_map[engine]
    nav = Navigation(driver).open()
    nav.init_and_click_awesome_bar_with_engine(engine)
    nav.verify_shard_text(engine_shard)
