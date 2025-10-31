import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028799"


SEARCH_ENGINES = [
    "@google",
    "@bing",
    "@duckduckgo",
    "@wikipedia",
]


@pytest.mark.smoke
def test_no_search_engine_suggestions_in_private_window(driver: Firefox):
    """
    C3028799 - Verify that in a New Private Window, after selecting a search shortcut,
    suggestions from that search engine are NOT displayed while typing a query.
    """
    # Open Private Window
    panel = PanelUi(driver)
    panel.open_and_switch_to_new_window("private")

    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")  # kept for parity / future use

    for shortcut in SEARCH_ENGINES:
        # Open a new tab for each shortcut
        nav.open_and_switch_to_new_window("tab")

        # Activate search mode using the shortcut
        nav.clear_awesome_bar()
        try:
            nav.search(shortcut)
        except Exception:
            nav.type_in_awesome_bar(shortcut + Keys.ENTER)

        # Type a query and verify there are no external search suggestions
        has_no_external_suggestions = nav.search_and_check_no_external_suggestions(
            text="random",
            search_mode="awesome",
            max_rows=3,  # allow small internal items like history/bookmarks
        )

        assert has_no_external_suggestions, (
            f"External search suggestions appeared for {shortcut} in Private Window."
        )

        nav.clear_awesome_bar()
