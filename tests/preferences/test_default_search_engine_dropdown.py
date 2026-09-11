import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

NEW_ENGINE = "DuckDuckGo"


@pytest.fixture()
def about_prefs_category():
    return "search"


@pytest.fixture()
def test_case():
    return "4105787"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_default_search_engine_dropdown(
    driver: Firefox, about_prefs: AboutPrefs, nav: Navigation, tabs: TabBar
):
    """
    C4105787 - The Default search engine drop-down works as expected.
    """
    about_prefs.open()

    # Step 2: Every enabled engine from Search shortcuts is offered in the dropdown.
    enabled_engines = about_prefs.get_enabled_search_engines()
    options = about_prefs.get_default_engine_dropdown_options()
    assert set(enabled_engines) == set(options), (
        f"Dropdown shows {options}, expected the enabled engines {enabled_engines}"
    )

    # Step 3: Pick a different default and confirm the search pane agrees.
    about_prefs.search_engine_dropdown().select_option(NEW_ENGINE)
    about_prefs.wait_for_default_search_engine(NEW_ENGINE)

    # The unified search button names the new default in its l10n args.
    tabs.new_tab_by_button()
    nav.element_attribute_contains("searchmode-switcher", "data-l10n-args", NEW_ENGINE)
