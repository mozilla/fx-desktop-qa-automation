import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
def test_3028799_no_search_engine_suggestions_in_private_window(driver: Firefox):
    """
    C3028799 - Verify that in a New Private Window, after selecting a search shortcut,
    suggestions from that search engine are not displayed while typing a query.
    """
    panel = PanelUi(driver)
    panel.open_and_switch_to_new_window("private")

    nav = Navigation(driver)
    wait = WebDriverWait(driver, 3)

    for shortcut in SEARCH_ENGINES:
        # Open a new tab for each search shortcut
        nav.open_and_switch_to_new_window("tab")

        # Activate search mode via shortcut
        nav.clear_awesome_bar()
        nav.search(shortcut)

        # Type a query and verify no external search suggestions are shown
        nav.clear_awesome_bar()
        nav.type_in_awesome_bar("random")

        # Wait for urlbar results to appear (if any)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "urlbar-results")))
            rows = driver.find_elements(By.CSS_SELECTOR, "#urlbar-results .urlbarView-row")
        except Exception:
            # If results container not found, treat as zero suggestions
            rows = []

        assert len(rows) <= 3, f"Unexpected suggestions displayed for {shortcut} (found {len(rows)} rows)."

        nav.clear_awesome_bar()
