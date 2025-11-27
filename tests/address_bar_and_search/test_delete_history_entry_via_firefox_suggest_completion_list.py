import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, PanelUi, TabBar

# @pytest.fixture()
# def use_profile():
#     return "theme_change"


@pytest.fixture()
def test_case():
    return "3028901"


YOUTUBE_URL = "https://www.youtube.com/"
FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"

WEBSITES = [YOUTUBE_URL, FACEBOOK_URL, AMAZON_URL]
SEARCH_TERM = "you"
HISTORY_ENTRY = "YouTube"


def test_delete_history_from_url_bar_completion_list(driver: Firefox):
    """
    C3028901 Verify that deleting an entry from the Firefox Suggest completion list also removes the same entry from
    the History menu.
    """
    # Initialize page objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)

    for url in WEBSITES:
        driver.get(url)

    # Ensure the targeted entry is visible in History menu
    panel.verify_history_item_exists(HISTORY_ENTRY)

    # tabs.new_tab_by_button()
    # tabs.switch_to_new_tab()

    # Type into the URL bar to trigger suggestions
    nav.type_in_awesome_bar(SEARCH_TERM)
    nav.wait_for_suggestions_present()

    # Select the suggestion and delete using Shift+Backspace
    nav.perform_key_combo_chrome(Keys.ARROW_DOWN)
    nav.perform_key_combo_chrome(Keys.SHIFT, Keys.BACKSPACE)

    # # Wait for the deleted suggestion to be removed from the list (using base page expect)
    # with nav.driver.context(nav.driver.CONTEXT_CHROME):
    #     nav.expect(
    #         lambda d: HISTORY_ENTRY not in
    #         [el.text for el in nav.get_elements("suggestion-titles")]
    #     )

    # Verify the entry is removed from History menu
    panel.verify_history_item_not_exists(HISTORY_ENTRY)
