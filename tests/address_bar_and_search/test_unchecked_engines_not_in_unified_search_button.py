import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

DISABLED_ENGINES = ["eBay", "Perplexity"]
MOVED_ENGINE = "Wikipedia (en)"


@pytest.fixture()
def test_case():
    return "3897585"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        ("browser.settings-redesign.enabled", True),
    ]


def usb_engines(nav: Navigation, location: str) -> list[str]:
    """Return the engine names in the urlbar or searchbar USB list."""
    return [
        engine.get_attribute("label")
        for engine in nav.get_elements(
            "search-mode-switcher-engines", labels=[location]
        )
    ]


def test_unchecked_engines_not_in_unified_search_button(driver: Firefox):
    """
    C3897585 - Unchecked search engines are not shown on Unified Search Button from search bar.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Step 1: Move one engine up to second place.
    prefs.open()
    engines = prefs.get_enabled_search_engines()
    # Selenium can't drag in this list, so use the move up shortcut.
    for position in range(engines.index(MOVED_ENGINE) - 1, 0, -1):
        row = prefs.get_element("search-shortcuts-engine-row", labels=[MOVED_ENGINE])
        row.send_keys(Keys.CONTROL, Keys.SHIFT, Keys.ARROW_UP)
        # Wait for each move before the next one.
        prefs.expect(
            lambda _: prefs.get_enabled_search_engines().index(MOVED_ENGINE) == position
        )
    engines.remove(MOVED_ENGINE)
    engines.insert(1, MOVED_ENGINE)

    # Step 1 (continued): Untick some engines.
    for engine in DISABLED_ENGINES:
        prefs.click_on("search-shortcuts-engine-toggle", labels=[engine])
        engines.remove(engine)
    prefs.expect(lambda _: prefs.get_enabled_search_engines() == engines)

    # Step 2: The address bar USB shows the new list.
    nav.add_search_bar_via_customizable_ui()
    tabs.open_and_switch_to_new_tab()
    nav.click_search_mode_switcher()
    nav.expect(lambda _: usb_engines(nav, "urlbar") == engines)
    nav.perform_key_combo_chrome(Keys.ESCAPE)

    # Step 2: The search bar USB shows the new list.
    nav.click_on("legacy-searchmode-switcher")
    nav.element_visible("searchbar-switcher-popup")
    nav.expect(lambda _: usb_engines(nav, "searchbar") == engines)
