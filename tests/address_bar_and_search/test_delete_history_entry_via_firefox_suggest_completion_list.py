import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, PanelUi


@pytest.fixture()
def test_case():
    return "3028901"


HISTORY_PAGES = [
    "https://www.imdb.com/",
    "https://www.youtube.com/",
    "https://www.nasa.gov/",
]

SEARCH_TERM = "you"
HISTORY_ENTRY = "YouTube"


def test_delete_history_from_url_bar_completion_list(driver: Firefox):
    """
    C3028901 - Verify that deleting an entry from the Firefox Suggest completion list also removes the same entry from
    the History menu.
    """
    # Initialize page objects
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Create history by navigating to each page sequentially
    for url in HISTORY_PAGES:
        driver.get(url)

    # Ensure the targeted entry is visible in History menu
    panel.verify_history_item_exists(HISTORY_ENTRY)

    # Type into the URL bar to trigger suggestions
    nav.type_in_awesome_bar(SEARCH_TERM)
    nav.wait_for_suggestions_present()

    # Select the suggestion and delete using Shift+Backspace
    nav.perform_key_combo_chrome(Keys.ARROW_DOWN)
    nav.perform_key_combo_chrome(Keys.SHIFT, Keys.BACKSPACE)

    # Verify the entry is removed from History menu
    panel.verify_history_item_not_exists(HISTORY_ENTRY)
