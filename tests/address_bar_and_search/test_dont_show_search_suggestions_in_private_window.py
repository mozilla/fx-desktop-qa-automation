import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi


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

    for shortcut in SEARCH_ENGINES:
        # Open a new tab for each shortcut
        nav.open_and_switch_to_new_window("tab")

        # Activate search mode for the current engine
        nav.clear_awesome_bar()
        nav.search(shortcut)

        # Type a query and verify that no external search suggestions appear
        has_no_external_suggestions = nav.verify_no_external_suggestions(
            text="random",
            search_mode="awesome",
            max_rows=3,  # allow small internal items like history/bookmarks
        )

        assert has_no_external_suggestions, (
            f"External search suggestions appeared for {shortcut} in Private Window."
        )

        nav.clear_awesome_bar()
